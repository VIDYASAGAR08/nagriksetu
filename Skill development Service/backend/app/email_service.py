"""
NagrikSetu Skill Development - Email Delivery Service
Handles genuine email dispatch via Python built-in smtplib and email.message.EmailMessage.
Supports Gmail SMTP (smtp.gmail.com:587) with STARTTLS authentication.
"""
import os
import smtplib
from email.message import EmailMessage
from typing import Tuple, Optional

# SMTP Configuration from Environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587").strip() or 587)
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "gundumani234@gmail.com").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME or "gundumani234@gmail.com").strip()

def is_smtp_configured() -> bool:
    """Check if Gmail SMTP credentials (username and app password) are configured."""
    return bool(SMTP_USERNAME and SMTP_PASSWORD)

def send_email_otp(recipient_email: str, otp_code: str, expiry_minutes: int = 5) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Send a 6-digit OTP to the recipient's email address using Python smtplib with Gmail SMTP.
    Returns (success, message_id_or_status, error_detail).
    """
    recipient = recipient_email.strip().lower()
    if not recipient or "@" not in recipient:
        return False, None, f"Invalid recipient email address: '{recipient_email}'"

    if not is_smtp_configured():
        return (
            False,
            None,
            "Gmail SMTP credentials not configured on server (SMTP_PASSWORD is unset). "
            "Please configure your Google App Password in backend .env to send real emails."
        )

    msg = EmailMessage()
    msg["Subject"] = f"{otp_code} is your NagrikSetu Registration Verification Code"
    msg["From"] = f"NagrikSetu <{SMTP_FROM_EMAIL}>"
    msg["To"] = recipient

    # Plaintext fallback content
    plain_text = f"""Dear Citizen,

Your verification code for NagrikSetu Skill Development registration is:

    {otp_code}

This code is valid for {expiry_minutes} minutes. Please do not share this code with anyone.

If you did not request this verification code, please ignore this email.

Regards,
NagrikSetu Skill Development Mission
Government Citizen Portal
"""
    msg.set_content(plain_text)

    # HTML formatted email body
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>NagrikSetu Verification Code</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f1f5f9; padding: 20px; margin: 0;">
  <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1; overflow: hidden;">
    <div style="background-color: #0f2444; padding: 20px; text-align: center;">
      <h2 style="color: #ffffff; margin: 0; font-size: 1.3rem; letter-spacing: 0.5px;">NagrikSetu Skill Development</h2>
      <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 0.85rem;">Citizen Registration Portal</p>
    </div>
    <div style="padding: 28px;">
      <p style="color: #1e293b; font-size: 1rem; margin-top: 0;">Dear Citizen,</p>
      <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
        Thank you for initiating registration on NagrikSetu. Please use the following 6-digit One-Time Password (OTP) to verify your email address:
      </p>
      <div style="text-align: center; margin: 24px 0;">
        <span style="display: inline-block; background-color: #f8fafc; border: 2px dashed #0f2444; border-radius: 8px; padding: 12px 28px; font-size: 2rem; font-weight: 700; letter-spacing: 6px; color: #0f2444;">
          {otp_code}
        </span>
      </div>
      <p style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">
        • This OTP is valid for <strong>{expiry_minutes} minutes</strong>.<br>
        • For security, never share this OTP with anyone.<br>
        • If you did not request this OTP, you can safely ignore this email.
      </p>
    </div>
    <div style="background-color: #f8fafc; padding: 14px 20px; text-align: center; border-top: 1px solid #e2e8f0;">
      <p style="color: #94a3b8; font-size: 0.78rem; margin: 0;">
        This is an automated system notification from NagrikSetu. Please do not reply directly to this email.
      </p>
    </div>
  </div>
</body>
</html>
"""
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20.0) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            return True, f"delivered_to_{recipient}", None
    except smtplib.SMTPAuthenticationError as e:
        return (
            False,
            None,
            f"Gmail SMTP authentication failed. Please verify that SMTP_USERNAME is correct "
            f"and SMTP_PASSWORD is a valid 16-character Google App Password (not your normal Google account password). Error: {str(e)}"
        )
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as e:
        return False, None, f"Failed to connect to Gmail SMTP server ({SMTP_HOST}:{SMTP_PORT}): {str(e)}"
    except smtplib.SMTPRecipientsRefused as e:
        return False, None, f"Recipient email address rejected by Gmail: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error while sending email via Gmail SMTP: {str(e)}"
