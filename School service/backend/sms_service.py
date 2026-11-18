import os
import re
import json
import logging
import secrets
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("nagriksetu.sms")

def load_local_env():
    """
    Loads environment variables from local .env files if present.
    Checks live volume mount (/app/data/.env), container root (/app/.env),
    and local directory paths.
    """
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
                            # Load from .env if not already set in environment
                            if k and v:
                                os.environ[k] = v
            except Exception as e:
                logger.debug(f"Failed to read env file at {path}: {e}")

# Initial load
load_local_env()

# Salt for hashing OTPs before database storage
OTP_SALT = os.getenv("OTP_SALT", "nagriksetu_secure_otp_salt_v1")

def normalize_phone_number(phone: str) -> str:
    """
    Normalizes a mobile number to 10-digit format for India.
    Accepts 10 digits, +91, 91, or formatted strings with spaces/hyphens.
    Returns 10-digit normalized phone number (e.g., '9876543210') or raises ValueError.
    """
    cleaned = re.sub(r'[\s\-\(\)\+]', '', str(phone).strip())
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith('0') and len(cleaned) == 11:
        cleaned = cleaned[1:]

    if not re.match(r'^[6-9]\d{9}$', cleaned):
        raise ValueError("Invalid phone number. Must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")

    return cleaned

def to_e164_indian(phone: str) -> str:
    """
    Converts a normalized 10-digit Indian mobile number into standard international
    E.164 format with '+' prefix (+91XXXXXXXXXX) required by OTP.dev.
    """
    clean_10 = normalize_phone_number(phone)
    return f"+91{clean_10}"

def to_msg91_format(phone: str) -> str:
    """
    Converts a normalized 10-digit Indian mobile number into MSG91 12-digit format (91XXXXXXXXXX).
    """
    clean_10 = normalize_phone_number(phone)
    return f"91{clean_10}"

def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(900000) + 100000)

def hash_otp(phone: str, otp: str) -> str:
    """
    Hash the OTP with salt and phone number using SHA-256
    to prevent rainbow table and pre-computation attacks.
    """
    clean_phone = normalize_phone_number(phone)
    salt = os.getenv("OTP_SALT", OTP_SALT)
    data = f"{clean_phone}:{otp}:{salt}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def verify_otp_hash(phone: str, otp: str, stored_hash: str) -> bool:
    """
    Secure constant-time verification of plain OTP against stored SHA-256 hash.
    """
    computed = hash_otp(phone, otp)
    return secrets.compare_digest(computed, stored_hash)

class SMSGatewayError(Exception):
    """Raised when the SMS Gateway fails to accept or process the dispatch request."""
    pass

class SMSConfigurationError(Exception):
    """Raised when the SMS provider credentials or required templates are missing."""
    pass

class BaseSMSProvider:
    """Abstract base class for SMS providers."""
    def send_otp(self, phone: str, otp: str) -> Dict[str, Any]:
        raise NotImplementedError

    def verify_otp(self, phone: str, otp: str) -> bool:
        """Optional online verification. Defaults to True if provider is send-only."""
        return True

class OTPDevSMSProvider(BaseSMSProvider):
    """
    Official OTP.dev SMS Provider Integration.
    API Documentation:
      Endpoint: https://api.otp.dev/v1/verifications
      Headers:
        X-OTP-Key: <OTPDEV_API_KEY>
        accept: application/json
        content-type: application/json
      Request Body (POST):
        {
          "data": {
            "channel": "sms",
            "sender": "<OTPDEV_SENDER_ID>",
            "phone": "+91XXXXXXXXXX",
            "template": "<OTPDEV_SMS_TEMPLATE_ID>",
            "code": "<6_DIGIT_OTP>",
            "code_length": 6
          }
        }
      Verification Endpoint (GET):
        https://api.otp.dev/v1/verifications?code=<CODE>&phone=<E.164_PHONE>
        Response HTTP 200 with non-empty "data": [...] on success,
        or empty "data": [] on invalid/expired code.
    """
    API_URL = "https://api.otp.dev/v1/verifications"

    def __init__(
        self,
        api_key: Optional[str] = None,
        sender_id: Optional[str] = None,
        template_id: Optional[str] = None
    ):
        load_local_env()
        self.api_key = (api_key or os.getenv("OTPDEV_API_KEY", "")).strip()
        self.sender_id = (sender_id or os.getenv("OTPDEV_SENDER_ID", "")).strip()
        self.template_id = (template_id or os.getenv("OTPDEV_SMS_TEMPLATE_ID", "")).strip()

    def validate_configuration(self):
        missing = []
        placeholders = (
            "YOUR_EXISTING_OTPDEV_API_KEY", "your_existing_otpdev_api_key", "your_otpdev_api_key_here",
            "YOUR_EXISTING_SENDER_UUID", "your_existing_sender_uuid", "your_otpdev_sender_id_here",
            "YOUR_EXISTING_TEMPLATE_UUID", "your_existing_template_uuid", "your_otpdev_template_id_here"
        )
        if not self.api_key or self.api_key in placeholders:
            missing.append("OTPDEV_API_KEY")
        if not self.sender_id or self.sender_id in placeholders:
            missing.append("OTPDEV_SENDER_ID")
        if not self.template_id or self.template_id in placeholders:
            missing.append("OTPDEV_SMS_TEMPLATE_ID")

        if missing:
            raise SMSConfigurationError(
                f"OTP.dev SMS Gateway configuration incomplete. Missing required environment variables: {', '.join(missing)}. "
                f"Please configure them in backend/.env file."
            )

    def send_otp(self, phone: str, otp: str) -> Dict[str, Any]:
        self.validate_configuration()

        clean_10 = normalize_phone_number(phone)
        e164_phone = to_e164_indian(clean_10)
        masked_phone = f"+91-******{clean_10[-4:]}"

        payload = {
            "data": {
                "channel": "sms",
                "sender": self.sender_id,
                "phone": e164_phone,
                "template": self.template_id,
                "code": str(otp),
                "code_length": 6
            }
        }
        req_body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.API_URL,
            data=req_body,
            headers={
                "X-OTP-Key": self.api_key,
                "accept": "application/json",
                "content-type": "application/json",
                "User-Agent": "NagrikSetu-SchoolService/2.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_text = resp.read().decode("utf-8")
                resp_data = json.loads(resp_text) if resp_text else {}
                
                # Check for error payload if present
                if str(resp_data.get("type", "")).lower() == "error":
                    err_msg = resp_data.get("message", "OTP.dev rejected verification request.")
                    logger.error(f"OTP.dev API error for recipient {masked_phone}: {err_msg}")
                    raise SMSGatewayError(f"SMS Gateway Error: {err_msg}")

                message_id = (
                    resp_data.get("message_id")
                    or resp_data.get("data", {}).get("message_id")
                    or resp_data.get("id")
                )
                logger.info(f"OTP.dev verification created for {masked_phone}. Message ID: {message_id or 'N/A'}")
                return {
                    "success": True,
                    "provider": "otpdev",
                    "request_id": message_id,
                    "message": "OTP dispatched successfully via OTP.dev SMS gateway."
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"OTP.dev HTTP Error {e.code} for {masked_phone}")
            try:
                err_json = json.loads(error_body)
                err_detail = err_json.get("message") or err_json.get("detail") or err_json.get("error") or str(e)
            except Exception:
                err_detail = error_body or str(e)
            
            if e.code == 401:
                raise SMSGatewayError("OTP.dev Authentication Failed: Invalid or expired OTPDEV_API_KEY. Please verify your X-OTP-Key.")
            elif e.code == 422:
                raise SMSGatewayError(f"OTP.dev Validation Error (HTTP 422): {err_detail}")
            elif e.code == 429:
                raise SMSGatewayError("OTP.dev Rate Limit Exceeded. Please try again later.")
            else:
                raise SMSGatewayError(f"OTP.dev HTTP Error ({e.code}): {err_detail}")
        except urllib.error.URLError as e:
            logger.error(f"OTP.dev connection error: {e.reason}")
            raise SMSGatewayError(f"Unable to connect to OTP.dev SMS Gateway: {e.reason}")
        except json.JSONDecodeError:
            raise SMSGatewayError("Unexpected non-JSON response from OTP.dev SMS Gateway.")

    def verify_otp(self, phone: str, otp: str) -> bool:
        """
        Validates OTP using official OTP.dev GET /v1/verifications endpoint.
        Returns True if code is valid (data array is non-empty).
        Returns False if code is invalid or expired.
        """
        self.validate_configuration()

        clean_10 = normalize_phone_number(phone)
        e164_phone = to_e164_indian(clean_10)

        query = urllib.parse.urlencode({"code": str(otp).strip(), "phone": e164_phone})
        url = f"{self.API_URL}?{query}"

        req = urllib.request.Request(
            url,
            headers={
                "X-OTP-Key": self.api_key,
                "accept": "application/json",
                "User-Agent": "NagrikSetu-SchoolService/2.0"
            },
            method="GET"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_text = resp.read().decode("utf-8")
                resp_data = json.loads(resp_text) if resp_text else {}
                data_list = resp_data.get("data", [])
                return isinstance(data_list, list) and len(data_list) > 0
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise SMSGatewayError("OTP.dev Authentication Failed: Invalid or expired OTPDEV_API_KEY.")
            return False
        except Exception as e:
            logger.error(f"OTP.dev online verification error: {e}")
            raise SMSGatewayError(f"Failed to verify OTP with OTP.dev: {str(e)}")


class MSG91SMSProvider(BaseSMSProvider):
    """
    Official MSG91 OTP API Provider integration (v5 SendOTP).
    """
    API_URL = "https://control.msg91.com/api/v5/otp"

    def __init__(self, auth_key: Optional[str] = None, template_id: Optional[str] = None, sender_id: Optional[str] = None):
        load_local_env()
        self.auth_key = (auth_key or os.getenv("MSG91_AUTH_KEY", "")).strip()
        self.template_id = (template_id or os.getenv("MSG91_TEMPLATE_ID", "")).strip()
        self.sender_id = (sender_id or os.getenv("MSG91_SENDER_ID", "")).strip()

    def validate_configuration(self):
        missing = []
        if not self.auth_key or self.auth_key in ("your_msg91_auth_key_here", "PASTE_YOUR_AUTH_KEY_HERE"):
            missing.append("MSG91_AUTH_KEY")
        if not self.template_id or self.template_id in ("your_msg91_dlt_template_id_here", "PASTE_YOUR_TEMPLATE_ID_HERE"):
            missing.append("MSG91_TEMPLATE_ID")
        if missing:
            raise SMSConfigurationError(
                f"MSG91 SMS Gateway configuration incomplete. Missing required environment variables: {', '.join(missing)}. "
                f"Please configure them in backend/.env file."
            )

    def send_otp(self, phone: str, otp: str) -> Dict[str, Any]:
        self.validate_configuration()

        clean_10 = normalize_phone_number(phone)
        msg91_mobile = to_msg91_format(clean_10)
        masked_phone = f"+91-******{clean_10[-4:]}"

        query_params = {
            "template_id": self.template_id,
            "mobile": msg91_mobile,
            "otp": str(otp),
            "otp_expiry": "5"
        }
        encoded_query = urllib.parse.urlencode(query_params)
        request_url = f"{self.API_URL}?{encoded_query}"

        req_body = json.dumps({}).encode("utf-8")
        req = urllib.request.Request(
            request_url,
            data=req_body,
            headers={
                "authkey": self.auth_key,
                "content-type": "application/json",
                "User-Agent": "NagrikSetu-SchoolService/2.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_text = resp.read().decode("utf-8")
                resp_data = json.loads(resp_text) if resp_text else {}
                
                resp_type = str(resp_data.get("type", "")).lower()
                if resp_type == "error":
                    error_msg = resp_data.get("message", "MSG91 rejected OTP request.")
                    logger.error(f"MSG91 API error for recipient {masked_phone}: {error_msg}")
                    raise SMSGatewayError(f"SMS Gateway Error: {error_msg}")

                req_id = resp_data.get("request_id")
                logger.info(f"MSG91 OTP accepted successfully for recipient {masked_phone}. Request ID: {req_id or 'N/A'}")
                return {
                    "success": True,
                    "provider": "msg91",
                    "request_id": req_id,
                    "message": "OTP dispatched successfully via MSG91 SMS gateway."
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"MSG91 HTTP Error {e.code} for {masked_phone}")
            try:
                err_json = json.loads(error_body)
                err_detail = err_json.get("message") or err_json.get("detail") or str(e)
            except Exception:
                err_detail = error_body or str(e)
            
            if e.code == 401:
                raise SMSGatewayError("MSG91 Authentication Failed: Invalid or expired MSG91_AUTH_KEY. Please verify your MSG91 Auth Key.")
            elif e.code == 422:
                raise SMSGatewayError(f"MSG91 Validation Error (HTTP 422): {err_detail}")
            elif e.code == 429:
                raise SMSGatewayError("MSG91 Gateway Rate Limit Exceeded. Please try again later.")
            else:
                raise SMSGatewayError(f"SMS Gateway HTTP Error ({e.code}): {err_detail}")
        except urllib.error.URLError as e:
            logger.error(f"MSG91 connection error: {e.reason}")
            raise SMSGatewayError(f"Unable to connect to SMS Gateway: {e.reason}")
        except json.JSONDecodeError:
            raise SMSGatewayError("Unexpected non-JSON response from SMS Gateway.")


class MockSMSProvider(BaseSMSProvider):
    """
    Development SMS Provider for student-project and staging environments.
    Simulates SMS OTP delivery without contacting OTP.dev or sending real SMS.
    Safely logs dispatch action without exposing the plain OTP value.
    """
    def send_otp(self, phone: str, otp: str) -> Dict[str, Any]:
        clean_10 = normalize_phone_number(phone)
        masked_phone = f"+91-******{clean_10[-4:]}"
        logger.info(f"[DEV_SIMULATION] Simulated SMS OTP generated for recipient {masked_phone}.")
        return {
            "success": True,
            "provider": "mock",
            "is_simulated": True,
            "request_id": f"dev_sim_{secrets.token_hex(6)}",
            "message": "Simulated SMS OTP generated for student development environment (no real SMS sent)."
        }

    def verify_otp(self, phone: str, otp: str) -> bool:
        """Development simulation relies entirely on local salted SHA-256 database verification."""
        return True


def is_development_sms_mode() -> bool:
    """
    Checks if development-mode simulated SMS is active.
    Returns True if OTP_PROVIDER or SMS_PROVIDER is 'mock', 'dev', 'development', 'simulated', or 'local'.
    """
    load_local_env()
    provider_name = (os.getenv("OTP_PROVIDER") or os.getenv("SMS_PROVIDER") or "").strip().lower()
    return provider_name in ("mock", "dev", "development", "simulated", "local")


def get_sms_provider() -> BaseSMSProvider:
    """Factory returning configured SMS provider instance."""
    load_local_env()
    # Check OTP_PROVIDER first, fallback to SMS_PROVIDER, default to mock
    provider_name = (os.getenv("OTP_PROVIDER") or os.getenv("SMS_PROVIDER") or "mock").strip().lower()
    if provider_name in ("mock", "dev", "development", "simulated", "local"):
        return MockSMSProvider()
    elif provider_name in ("otpdev", "otp.dev"):
        return OTPDevSMSProvider()
    elif provider_name == "msg91":
        return MSG91SMSProvider()
    else:
        raise SMSConfigurationError(
            f"Unsupported SMS provider: '{provider_name}'. Supported providers: 'mock', 'otpdev', 'msg91'"
        )

def send_otp_sms(phone_number: str, otp: str) -> Dict[str, Any]:
    """
    Main public function to send an OTP via the configured SMS provider.
    Validates mobile format, initializes provider, dispatches OTP without exposing secrets in logs.
    """
    clean_phone = normalize_phone_number(phone_number)
    provider = get_sms_provider()
    return provider.send_otp(clean_phone, otp)

def verify_otp_with_provider(phone_number: str, otp: str) -> bool:
    """
    Calls server-side verification on provider if supported (e.g. OTP.dev).
    Returns True if valid or if provider is send-only / mock.
    """
    clean_phone = normalize_phone_number(phone_number)
    provider = get_sms_provider()
    return provider.verify_otp(clean_phone, otp)
