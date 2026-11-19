"""
NagrikSetu Skill Development - OTP Verification Service
Supports secure 6-digit generation (secrets), SHA-256 code hashing, 5-minute expiry,
5-attempt limits, 60-second cooldowns, demo mode support, and email/SMS dispatch.
"""
import os
import re
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from app.models import OTPVerificationSession
from app.email_service import send_email_otp, is_smtp_configured, SMTP_USERNAME

# Environment settings
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
OTP_DEMO_MODE_RAW = os.getenv("OTP_DEMO_MODE", "false").strip().lower()

# Verification Security Policy
OTP_EXPIRY_MINUTES = 5
RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5

def is_demo_mode_active() -> bool:
    """
    Demo mode is ONLY allowed if APP_ENV != 'production' and OTP_DEMO_MODE == 'true'.
    Demo mode is strictly rejected in production environments.
    """
    if APP_ENV == "production":
        return False
    return OTP_DEMO_MODE_RAW in ("true", "1", "yes")

def normalize_phone(phone: str) -> str:
    """Normalize phone number to 10-digit Indian mobile number."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        return digits
    if digits.startswith("91") and len(digits) == 12:
        return digits[2:]
    if digits.startswith("0") and len(digits) == 11:
        return digits[1:]
    return digits

def normalize_email(email: str) -> str:
    """Normalize email address to lowercase stripped string."""
    return (email or "").strip().lower()

def is_valid_email(email: str) -> bool:
    """Basic validation for standard email address format."""
    email_clean = normalize_email(email)
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email_clean))

def generate_reference() -> str:
    """Generate a high-entropy random verification session token."""
    return f"otp_ref_{secrets.token_hex(16)}"

def generate_otp_code(length: int = 6) -> str:
    """
    Generate a cryptographically secure 6-digit numeric OTP using Python secrets module.
    Produces values from 100000 to 999999.
    """
    return f"{secrets.randbelow(900000) + 100000:06d}"

def hash_otp_code(code: str) -> str:
    """Compute SHA-256 hash of OTP code for secure database persistence."""
    return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()

def is_configured() -> bool:
    """Check if valid Gmail SMTP credentials are configured (or demo mode is active)."""
    if is_demo_mode_active():
        return True
    return is_smtp_configured()

def get_active_provider_name() -> str:
    """Return human-readable active provider name."""
    if is_demo_mode_active():
        return "Gmail SMTP (Demo Mode)"
    return "Gmail SMTP"

def dispatch_registration_email_otp(recipient_email: str, otp_code: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Dispatch OTP to recipient email.
    If demo mode is active, skips external SMTP network call and returns demo token.
    Otherwise sends real email using Python smtplib to smtp.gmail.com.
    Returns (success, message_id, error_detail, demo_otp_or_none).
    """
    clean_email = normalize_email(recipient_email)
    if not is_valid_email(clean_email):
        return False, None, f"Invalid email address: '{recipient_email}'", None

    # Handle Development Demo Mode
    if is_demo_mode_active():
        return True, f"demo_mode_{clean_email}", None, otp_code

    # Real Gmail SMTP Mode
    success, msg_id, err_detail = send_email_otp(clean_email, otp_code, OTP_EXPIRY_MINUTES)
    return success, msg_id, err_detail, None
