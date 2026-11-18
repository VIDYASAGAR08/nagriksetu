import os
import re
import json
import logging
import secrets
import hashlib
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from typing import Dict, Any, Optional

logger = logging.getLogger("nagriksetu.email")

def load_local_env():
    """
    Loads environment variables from local .env files if present.
    Checks live volume mount (/app/data/.env), container root (/app/.env),
    and local directory paths.
    """
    candidates = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "data", ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        "/app/data/.env",
        "/app/.env",
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
                            # If unset or currently empty string, assign from file
                            if k and v and (not os.environ.get(k) or os.environ.get(k).strip() == ""):
                                os.environ[k] = v
            except Exception as e:
                logger.debug(f"Failed to read env file at {path}: {e}")

load_local_env()

EMAIL_SALT = os.getenv("OTP_SALT", "nagriksetu_secure_otp_salt_v1")

def normalize_email(email: str) -> str:
    """
    Normalizes email address by trimming whitespace and lowercasing.
    Validates format using standard email regex.
    """
    cleaned = str(email).strip().lower()
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', cleaned):
        raise ValueError("Invalid email address format.")
    return cleaned

def mask_email(email: str) -> str:
    """Masks email for safe logging (e.g. c***n@example.com)."""
    try:
        parts = email.split("@")
        name = parts[0]
        domain = parts[1]
        if len(name) <= 2:
            masked_name = name[0] + "*"
        else:
            masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
        return f"{masked_name}@{domain}"
    except Exception:
        return "******@masked"

def generate_email_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(900000) + 100000)

def hash_email_otp(email: str, otp: str) -> str:
    """Hash the OTP with salt and normalized email using SHA-256."""
    clean_email = normalize_email(email)
    salt = os.getenv("OTP_SALT", EMAIL_SALT)
    data = f"{clean_email}:{otp}:{salt}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def verify_email_otp_hash(email: str, otp: str, stored_hash: str) -> bool:
    """Constant-time verification of email OTP against stored SHA-256 hash."""
    computed = hash_email_otp(email, otp)
    return secrets.compare_digest(computed, stored_hash)

class EmailConfigurationError(Exception):
    """Raised when email provider credentials or server settings are missing."""
    pass

class EmailDeliveryError(Exception):
    """Raised when email dispatch fails."""
    pass

class BaseEmailProvider:
    def send_email(self, to_email: str, subject: str, body_text: str, body_html: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

class SMTPEmailProvider(BaseEmailProvider):
    """
    Standard SMTP Email Provider.
    Supports STARTTLS (port 587) and SSL (port 465).
    """
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        load_local_env()
        self.host = (host or os.getenv("SMTP_HOST", "")).strip()
        port_raw = port or os.getenv("SMTP_PORT", "587")
        try:
            self.port = int(str(port_raw).strip())
        except ValueError:
            self.port = 587
        self.username = (username or os.getenv("SMTP_USERNAME", "")).strip()
        self.password = (password or os.getenv("SMTP_PASSWORD", "")).strip()
        self.from_email = (from_email or os.getenv("SMTP_FROM_EMAIL", "")).strip()
        self.from_name = (from_name or os.getenv("SMTP_FROM_NAME", "NagrikSetu")).strip()

    def validate_configuration(self):
        missing = []
        placeholders = (
            "your_smtp_host", "your_smtp_username", "your_smtp_password",
            "your_from_email", "YOUR_SMTP_HOST", "YOUR_SMTP_USERNAME",
            "YOUR_SMTP_PASSWORD", "YOUR_FROM_EMAIL"
        )
        if not self.host or self.host in placeholders:
            missing.append("SMTP_HOST")
        if not self.username or self.username in placeholders:
            missing.append("SMTP_USERNAME")
        if not self.password or self.password in placeholders:
            missing.append("SMTP_PASSWORD")
        if not self.from_email or self.from_email in placeholders:
            missing.append("SMTP_FROM_EMAIL")

        if missing:
            raise EmailConfigurationError(
                f"SMTP Email Gateway configuration incomplete. Missing required environment variables: {', '.join(missing)}. "
                f"Please configure them in backend/.env file."
            )

    def send_email(self, to_email: str, subject: str, body_text: str, body_html: Optional[str] = None) -> Dict[str, Any]:
        self.validate_configuration()
        clean_to = normalize_email(to_email)
        masked = mask_email(clean_to)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = clean_to
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))

        try:
            ssl_ctx = ssl.create_default_context()
            if self.port == 465:
                # SSL connection
                with smtplib.SMTP_SSL(self.host, self.port, timeout=15, context=ssl_ctx) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.from_email, [clean_to], msg.as_string())
            else:
                # TLS connection (port 587 or 25)
                with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                    server.ehlo()
                    server.starttls(context=ssl_ctx)
                    server.ehlo()
                    server.login(self.username, self.password)
                    server.sendmail(self.from_email, [clean_to], msg.as_string())

            logger.info(f"Email successfully dispatched to recipient {masked} with subject '{subject}'.")
            return {
                "success": True,
                "provider": "smtp",
                "message": f"Email dispatched successfully to {masked}."
            }
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failure for {masked}")
            raise EmailDeliveryError(
                "SMTP Authentication Failed: Invalid username or password (535 Bad Credentials). "
                "For Gmail, please verify that 2-Step Verification is active and you are using a generated 16-character App Password."
            )
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP server disconnected for {masked}: {e}")
            raise EmailDeliveryError(
                "SMTP Server Disconnected: The mail server dropped the connection unexpectedly during authentication. "
                "For Gmail, this typically occurs when the provided credentials or App Password are not accepted (535 Bad Credentials)."
            )
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error for {masked}: {e}")
            raise EmailDeliveryError(f"SMTP Delivery Error: {str(e)}")
        except Exception as e:
            logger.error(f"SMTP connection error: {e}")
            raise EmailDeliveryError(f"Unable to connect to SMTP server: {str(e)}")

def get_email_provider() -> BaseEmailProvider:
    """Factory returning configured Email provider instance."""
    load_local_env()
    provider_name = os.getenv("EMAIL_PROVIDER", "smtp").strip().lower()
    if provider_name == "smtp":
        return SMTPEmailProvider()
    else:
        raise EmailConfigurationError(f"Unsupported email provider: '{provider_name}'. Supported providers: 'smtp'")

def send_registration_otp_email(to_email: str, otp: str, full_name: Optional[str] = None) -> Dict[str, Any]:
    """Sends 6-digit registration OTP to recipient email."""
    name_display = (full_name or "Citizen").strip()
    subject = "NagrikSetu - Email Verification Code"
    body_text = f"""Namaskara {name_display},

Thank you for registering on NagrikSetu - Karnataka Public Education Discovery & Services Portal.

Your verification code is: {otp}

This code is valid for 5 minutes. For your security, do not share this code with anyone.

Department of School Education & Literacy
Government of Karnataka
"""
    body_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 2rem;">
  <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #d0d5dd; padding: 2rem;">
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <h2 style="color: #1a3a6b; margin: 0;">NagrikSetu</h2>
      <p style="color: #4b5563; font-size: 0.875rem; margin-top: 0.25rem;">Government of Karnataka Public Education Services</p>
    </div>
    <p style="color: #1e293b; font-size: 1rem;">Namaskara <strong>{name_display}</strong>,</p>
    <p style="color: #334155; font-size: 0.9375rem; line-height: 1.5;">Please use the following single-use verification code to complete your Citizen account registration:</p>
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 1.25rem; text-align: center; margin: 1.5rem 0;">
      <span style="font-size: 2rem; font-weight: 800; letter-spacing: 0.3em; color: #15803d; font-family: monospace;">{otp}</span>
    </div>
    <p style="color: #64748b; font-size: 0.8125rem;">This code is valid for <strong>5 minutes</strong>. If you did not request this registration, please disregard this email.</p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0;" />
    <p style="color: #94a3b8; font-size: 0.75rem; text-align: center; margin: 0;">Department of School Education & Literacy · Government of Karnataka</p>
  </div>
</body>
</html>
"""
    provider = get_email_provider()
    return provider.send_email(to_email, subject, body_text, body_html)

def send_login_otp_email(to_email: str, otp: str, full_name: Optional[str] = None) -> Dict[str, Any]:
    """Sends 6-digit login verification OTP to recipient email."""
    name_display = (full_name or "Citizen").strip()
    subject = "NagrikSetu - Sign In Verification Code"
    body_text = f"""Namaskara {name_display},

Your single-use sign-in verification code for NagrikSetu is: {otp}

This code is valid for 5 minutes. For your security, do not share this code with anyone.

Department of School Education & Literacy
Government of Karnataka
"""
    body_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 2rem;">
  <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #d0d5dd; padding: 2rem;">
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <h2 style="color: #1a3a6b; margin: 0;">NagrikSetu</h2>
      <p style="color: #4b5563; font-size: 0.875rem; margin-top: 0.25rem;">Government of Karnataka Public Education Services</p>
    </div>
    <p style="color: #1e293b; font-size: 1rem;">Namaskara <strong>{name_display}</strong>,</p>
    <p style="color: #334155; font-size: 0.9375rem; line-height: 1.5;">Please use the following single-use verification code to sign in to your Citizen account:</p>
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 1.25rem; text-align: center; margin: 1.5rem 0;">
      <span style="font-size: 2rem; font-weight: 800; letter-spacing: 0.3em; color: #15803d; font-family: monospace;">{otp}</span>
    </div>
    <p style="color: #64748b; font-size: 0.8125rem;">This code is valid for <strong>5 minutes</strong>. If you did not request this sign-in attempt, please secure your account immediately.</p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0;" />
    <p style="color: #94a3b8; font-size: 0.75rem; text-align: center; margin: 0;">Department of School Education & Literacy · Government of Karnataka</p>
  </div>
</body>
</html>
"""
    provider = get_email_provider()
    return provider.send_email(to_email, subject, body_text, body_html)

def send_password_reset_email(to_email: str, reset_url: str, full_name: Optional[str] = None) -> Dict[str, Any]:
    """Sends password reset link to recipient email."""
    name_display = (full_name or "User").strip()
    subject = "NagrikSetu - Password Reset Request"
    body_text = f"""Namaskara {name_display},

We received a request to reset your NagrikSetu account password.

To choose a new password, open the following link in your browser:
{reset_url}

This link is valid for 1 hour. If you did not request a password reset, please ignore this email.

Department of School Education & Literacy
Government of Karnataka
"""
    body_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 2rem;">
  <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #d0d5dd; padding: 2rem;">
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <h2 style="color: #1a3a6b; margin: 0;">NagrikSetu</h2>
      <p style="color: #4b5563; font-size: 0.875rem; margin-top: 0.25rem;">Account Security Service</p>
    </div>
    <p style="color: #1e293b; font-size: 1rem;">Namaskara <strong>{name_display}</strong>,</p>
    <p style="color: #334155; font-size: 0.9375rem; line-height: 1.5;">We received a request to reset your password. Click the button below to set a new password:</p>
    <div style="text-align: center; margin: 1.75rem 0;">
      <a href="{reset_url}" style="background: #1a3a6b; color: #ffffff; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block;">Reset Password →</a>
    </div>
    <p style="color: #64748b; font-size: 0.8125rem;">This link is valid for <strong>1 hour</strong>. If you did not request this, you can safely ignore this email.</p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0;" />
    <p style="color: #94a3b8; font-size: 0.75rem; text-align: center; margin: 0;">Department of School Education & Literacy · Government of Karnataka</p>
  </div>
</body>
</html>
"""
    provider = get_email_provider()
    return provider.send_email(to_email, subject, body_text, body_html)
