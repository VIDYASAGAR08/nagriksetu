main_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """        # 6. Dispatch Real Email OTP via Gmail SMTP
        is_dev = os.getenv("SMS_ENVIRONMENT", "").lower() == "development" or os.getenv("EMAIL_PROVIDER", "").lower() == "mock" or google_user.get("is_simulated", False)
        dev_notice = None
        dev_otp_val = None
        try:
            if purpose == "login":
                send_login_otp_email(verified_email, otp, account_name)
            else:
                send_registration_otp_email(verified_email, otp, account_name)
        except (EmailConfigurationError, EmailDeliveryError) as ede:
            logging.getLogger("nagriksetu.auth").warning(f"Gmail SMTP delivery failed: {ede}")
            if is_dev:
                dev_notice = f"Gmail SMTP dispatch encountered an error: {str(ede)[:100]}. Development OTP fallback active."
                dev_otp_val = otp
            else:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ede))
        except Exception as e:
            logging.getLogger("nagriksetu.auth").error(f"Unexpected email dispatch error: {e}")
            if is_dev:
                dev_notice = f"Email connection error: {str(e)[:100]}. Development OTP fallback active."
                dev_otp_val = otp
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email dispatch error: {str(e)}")

        with conn:
            conn.execute(
                \"\"\"
                INSERT INTO email_otps (
                    otp_id, email, otp_hash, purpose, attempts, max_attempts,
                    is_used, expires_at, created_at, ip_address
                ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                \"\"\",
                (otp_id, verified_email, otp_hash, purpose, expires_at, created_at_str, client_ip)
            )

        masked_target = mask_email(verified_email)
        resp = {
            "success": True,
            "message": f"Verification code sent to {masked_target}.",
            "email": verified_email,
            "masked_email": masked_target,
            "google_name": google_name,
            "delivery_channel": "Email",
            "purpose": purpose,
            "resend_cooldown_seconds": 60,
            "expires_in_seconds": 300,
        }
        if dev_notice:
            resp["dev_notice"] = dev_notice
            resp["dev_otp"] = dev_otp_val
            resp["dev_mode"] = True
        return resp"""

new_block = """        # 6. Dispatch Real Email OTP via Gmail SMTP
        # Email OTP must be accepted by the SMTP provider before saving to DB or claiming success
        try:
            if purpose == "login":
                send_login_otp_email(verified_email, otp, account_name)
            else:
                send_registration_otp_email(verified_email, otp, account_name)
        except EmailConfigurationError as ece:
            logging.getLogger("nagriksetu.auth").error(f"Email gateway misconfigured: {ece}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Email configuration error: {str(ece)}")
        except EmailDeliveryError as ede:
            logging.getLogger("nagriksetu.auth").error(f"Email delivery rejected by SMTP: {ede}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Email delivery failed: {str(ede)}")
        except Exception as e:
            logging.getLogger("nagriksetu.auth").error(f"Unexpected email dispatch error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email dispatch error: {str(e)}")

        # Save to database ONLY AFTER email provider accepts message
        with conn:
            conn.execute(
                \"\"\"
                INSERT INTO email_otps (
                    otp_id, email, otp_hash, purpose, attempts, max_attempts,
                    is_used, expires_at, created_at, ip_address
                ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                \"\"\",
                (otp_id, verified_email, otp_hash, purpose, expires_at, created_at_str, client_ip)
            )

        masked_target = mask_email(verified_email)
        return {
            "success": True,
            "message": f"Verification code sent to {masked_target}.",
            "email": verified_email,
            "masked_email": masked_target,
            "google_name": google_name,
            "delivery_channel": "Email",
            "purpose": purpose,
            "resend_cooldown_seconds": 60,
            "expires_in_seconds": 300,
        }"""

assert old_block in content, "old_block not found in backend/main.py"
content = content.replace(old_block, new_block, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated backend/main.py email dispatch logic to strictly require SMTP acceptance before DB save or success!")
