with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """    if not req.otp_reference:
        raise HTTPException(
            status_code=400,
            detail="Mobile OTP verification required prior to submitting enrolment application. Please verify via SMS OTP."
        )

    otp_sess = db.query(OTPVerificationSession).filter(
        OTPVerificationSession.reference == req.otp_reference,
        OTPVerificationSession.purpose == "ENROLMENT",
        OTPVerificationSession.citizen_ref == user.citizen_ref,
        OTPVerificationSession.is_verified == True,
        OTPVerificationSession.is_consumed == False
    ).first()

    if not otp_sess:
        raise HTTPException(
            status_code=400,
            detail="Valid OTP verification not found for this enrolment submission. Please request and verify an OTP."
        )

    # Check expiry
    now_utc = datetime.now(timezone.utc)
    sess_exp = otp_sess.expires_at.replace(tzinfo=timezone.utc) if otp_sess.expires_at.tzinfo is None else otp_sess.expires_at
    if now_utc > sess_exp:
        raise HTTPException(
            status_code=400,
            detail="OTP verification session has expired. Please verify a new OTP."
        )

    # Mark OTP as consumed to prevent reuse
    otp_sess.is_consumed = True"""

replacement = """    # Mobile OTP verification requirement removed for seamless direct application submission
    # Normal 10-digit mobile number format validation is maintained
    if req.otp_reference:
        otp_sess = db.query(OTPVerificationSession).filter(
            OTPVerificationSession.reference == req.otp_reference,
            OTPVerificationSession.is_verified == True,
            OTPVerificationSession.is_consumed == False
        ).first()
        if otp_sess:
            otp_sess.is_consumed = True"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: submit_enrolment updated in host main.py")
else:
    print("ERROR: Target text block not found")
