import os
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional

logger = logging.getLogger("nagriksetu.sms")

# Salt for hashing OTPs before database storage
OTP_SALT = os.getenv("OTP_SALT", "nagriksetu_secure_otp_salt_v1")

def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(900000) + 100000)

def hash_otp(phone: str, otp: str) -> str:
    """Hash the OTP with salt and phone number to prevent rainbow table attacks."""
    data = f"{phone}:{otp}:{OTP_SALT}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def verify_otp_hash(phone: str, otp: str, stored_hash: str) -> bool:
    """Securely verify the plain OTP against the stored SHA-256 hash."""
    return hash_otp(phone, otp) == stored_hash

def dispatch_sms_otp(phone: str, otp: str, purpose: str = "register") -> Dict[str, Any]:
    """
    Dispatches OTP via SMS gateway or secure development mock.
    Identifies SMS provider status and logs cleanly.
    """
    sms_gateway_url = os.getenv("SMS_GATEWAY_URL")
    
    if sms_gateway_url:
        # Production SMS Gateway integration
        try:
            import urllib.request
            import json
            req_data = json.dumps({
                "phone": phone,
                "message": f"Your NagrikSetu verification code is {otp}. Valid for 5 minutes. Do not share this OTP with anyone.",
                "purpose": purpose
            }).encode("utf-8")
            req = urllib.request.Request(
                sms_gateway_url,
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "NagrikSetu-OTP/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                logger.info(f"Dispatched SMS OTP to {phone} via gateway. HTTP {resp.status}")
                return {
                    "sent": True,
                    "provider": "sms_gateway",
                    "channel_status": "live",
                    "message": "OTP sent via official SMS gateway."
                }
        except Exception as e:
            logger.error(f"Failed to dispatch SMS via gateway to {phone}: {e}")
            return {
                "sent": False,
                "provider": "sms_gateway",
                "channel_status": "error",
                "message": f"SMS gateway error: {str(e)}"
            }
    else:
        # Development environment mock with clear logging
        logger.info(
            f"[DEVELOPMENT SMS DISPATCH] Generated OTP for +91-{phone}: {otp} "
            f"(Purpose: {purpose}, Valid for 5 minutes). "
            f"Notice: SMS_GATEWAY_URL environment variable is not configured."
        )
        print(f"\n=======================================================")
        print(f" [NAGRIKSETU DEV SMS GATEWAY]")
        print(f" Recipient Phone: +91-{phone}")
        print(f" Verification OTP: {otp}")
        print(f" Valid for: 5 minutes | Purpose: {purpose}")
        print(f" (Live SMS provider not configured in environment)")
        print(f"=======================================================\n", flush=True)
        return {
            "sent": True,
            "provider": "development_mock",
            "channel_status": "dev_mock",
            "dev_otp": otp,  # Exposed for local testing verification when SMS_GATEWAY_URL is unset
            "message": "OTP generated and logged (Development mode: live SMS provider not configured)."
        }
