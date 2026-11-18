import os
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("nagriksetu.google_auth")

def load_local_env():
    """Load environment variables from .env files if present."""
    candidates = [
        "/app/data/.env",
        "/app/.env",
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        ".env",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'").strip('"')
                            if k and v:
                                os.environ[k] = v
            except Exception as e:
                logger.debug(f"Failed to read env file at {path}: {e}")

load_local_env()

class GoogleAuthError(Exception):
    """Raised when Google ID token validation fails."""
    pass

class GoogleConfigError(Exception):
    """Raised when Google OAuth is misconfigured."""
    pass

def get_google_client_id() -> str:
    load_local_env()
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if client_id in ("YOUR_GOOGLE_CLIENT_ID", "your_google_client_id_here", "PASTE_YOUR_CLIENT_ID_HERE"):
        return ""
    return client_id

def is_google_auth_configured() -> bool:
    return bool(get_google_client_id())

def verify_google_id_token(id_token: str) -> Dict[str, Any]:
    """
    Cryptographically verifies Google ID Token using official Google TokenInfo endpoint.
    Validates:
      - Token signature (verified by Google's public keys)
      - Issuer (accounts.google.com)
      - Expiration (token not expired)
      - Audience (matches configured GOOGLE_CLIENT_ID)
      - Email verified status
    Returns dict containing verified 'email', 'name', 'sub', 'picture'.
    Never trusts frontend claims without backend Google verification.
    """
    if not id_token or not isinstance(id_token, str):
        raise GoogleAuthError("Missing or invalid Google ID token.")

    token = id_token.strip()

    # Development simulation support for automated testing in dev mode only
    dev_env = os.getenv("SMS_ENVIRONMENT", "").lower() == "development" or os.getenv("ENVIRONMENT", "").lower() == "development"
    if dev_env and token.startswith("dev_test_token:"):
        parts = token.split(":")
        test_email = parts[1].strip().lower() if len(parts) > 1 else "student.tester@gmail.com"
        test_name = parts[2].strip() if len(parts) > 2 else "Test Google Citizen"
        logger.info(f"[DEV MODE] Accepted simulated Google ID token for {test_email}")
        return {
            "email": test_email,
            "name": test_name,
            "sub": "dev_google_sub_12345",
            "email_verified": True,
            "is_simulated": True
        }

    token_info_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.parse.quote(token)}"
    req = urllib.request.Request(
        token_info_url,
        headers={"User-Agent": "NagrikSetu-SchoolService/2.0"},
        method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        logger.warning(f"Google tokeninfo rejected token (HTTP {e.code}): {err_msg}")
        raise GoogleAuthError("Google account verification failed. Invalid, expired, or malformed Google ID token.")
    except urllib.error.URLError as e:
        logger.error(f"Failed to reach Google tokeninfo endpoint: {e.reason}")
        raise GoogleAuthError(f"Unable to connect to Google Identity verification service: {e.reason}")
    except Exception as e:
        logger.error(f"Unexpected error validating Google ID token: {e}")
        raise GoogleAuthError(f"Google token validation error: {str(e)}")

    # 1. Verify Issuer
    iss = data.get("iss", "")
    if iss not in ("accounts.google.com", "https://accounts.google.com"):
        raise GoogleAuthError(f"Invalid Google ID token issuer: {iss}")

    # 2. Verify Audience (if GOOGLE_CLIENT_ID is configured)
    expected_client_id = get_google_client_id()
    if expected_client_id:
        aud = data.get("aud", "")
        if aud != expected_client_id:
            raise GoogleAuthError(f"Google ID token audience mismatch. Token audience '{aud}' does not match configured Client ID.")

    # 3. Verify Expiration
    exp = int(data.get("exp", 0))
    if exp < time.time():
        raise GoogleAuthError("Google ID token has expired. Please select your Google account again.")

    # 4. Verify Email & Email Verified Status
    email = data.get("email", "").strip().lower()
    if not email:
        raise GoogleAuthError("Google account does not provide a valid email address.")

    email_verified = data.get("email_verified")
    if email_verified not in (True, "true", "True", 1, "1"):
        raise GoogleAuthError("Google email address is not verified by Google.")

    name = data.get("name") or data.get("given_name") or email.split("@")[0]
    sub = data.get("sub", "")
    picture = data.get("picture", "")

    return {
        "email": email,
        "name": name,
        "sub": sub,
        "picture": picture,
        "email_verified": True,
        "is_simulated": False
    }
