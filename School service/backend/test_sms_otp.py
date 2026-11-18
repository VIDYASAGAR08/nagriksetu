import os
import sys
import json
import uuid
import time
import sqlite3
import datetime
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock

# Import functions under test
from sms_service import (
    normalize_phone_number,
    to_e164_indian,
    to_msg91_format,
    generate_otp,
    hash_otp,
    verify_otp_hash,
    OTPDevSMSProvider,
    MSG91SMSProvider,
    SMSConfigurationError,
    SMSGatewayError,
    send_otp_sms,
    verify_otp_with_provider,
    get_sms_provider,
    load_local_env
)

def run_tests():
    print("==================================================")
    print("NAGRIKSETU SCHOOL SERVICE - OTP.DEV TEST SUITE")
    print("==================================================")
    passed = 0
    failed = 0

    def assert_true(condition, test_name):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {test_name}")
            passed += 1
        else:
            print(f"[FAIL] {test_name}")
            failed += 1

    # 1. Phone number normalization
    try:
        assert_true(normalize_phone_number("9876543210") == "9876543210", "Normalize plain 10-digit number")
        assert_true(normalize_phone_number("+919876543210") == "9876543210", "Normalize +91 prefix")
        assert_true(normalize_phone_number("919876543210") == "9876543210", "Normalize 91 prefix")
        assert_true(normalize_phone_number("09876543210") == "9876543210", "Normalize leading 0 prefix")
        assert_true(normalize_phone_number("98765 43210") == "9876543210", "Normalize space in number")
        assert_true(normalize_phone_number("+91-98765-43210") == "9876543210", "Normalize hyphens and formatting")
    except Exception as e:
        assert_true(False, f"Phone normalization tests raised: {e}")

    # 2. Invalid Indian mobile numbers rejected
    invalid_numbers = ["1234567890", "5987654321", "987654321", "98765432100", "abcdefghij"]
    for num in invalid_numbers:
        try:
            normalize_phone_number(num)
            assert_true(False, f"Should reject invalid number {num}")
        except ValueError:
            assert_true(True, f"Properly rejected invalid number {num}")

    # 3. OTP.dev E.164 format (+91XXXXXXXXXX)
    assert_true(to_e164_indian("9876543210") == "+919876543210", "Convert to E.164 with + prefix for OTP.dev")
    assert_true(to_msg91_format("9876543210") == "919876543210", "Convert to MSG91 12-digit format")

    # 4. Cryptographic 6-digit numeric OTP generation
    otps = [generate_otp() for _ in range(50)]
    all_6_digits = all(len(o) == 6 and o.isdigit() for o in otps)
    assert_true(all_6_digits, "Generated 50 unique cryptographically secure 6-digit OTPs")
    assert_true(len(set(otps)) > 45, "High entropy in generated OTP sequence")

    # 5. Salted SHA-256 OTP hashing and constant-time verification
    plain_otp = "482910"
    phone_test = "9876543210"
    h1 = hash_otp(phone_test, plain_otp)
    h2 = hash_otp(phone_test, plain_otp)
    h_wrong_phone = hash_otp("9876543211", plain_otp)
    assert_true(h1 == h2, "Deterministic hashing for identical phone and salt")
    assert_true(h1 != plain_otp, "Hashed value is not plain text")
    assert_true(h1 != h_wrong_phone, "Phone number is mixed into the cryptographic hash")
    assert_true(verify_otp_hash(phone_test, plain_otp, h1) is True, "Constant-time verification succeeds for matching OTP")
    assert_true(verify_otp_hash(phone_test, "111111", h1) is False, "Constant-time verification rejects incorrect OTP")

    # 6. OTP.dev provider configuration validation
    empty_provider = OTPDevSMSProvider(api_key="", sender_id="", template_id="")
    try:
        empty_provider.validate_configuration()
        assert_true(False, "Should raise SMSConfigurationError when credentials missing")
    except SMSConfigurationError as sce:
        assert_true(
            "OTPDEV_API_KEY" in str(sce) and "OTPDEV_SENDER_ID" in str(sce) and "OTPDEV_SMS_TEMPLATE_ID" in str(sce),
            "Detailed missing variable names in OTP.dev configuration error"
        )

    # Placeholder rejection
    placeholder_provider = OTPDevSMSProvider(
        api_key="YOUR_EXISTING_OTPDEV_API_KEY",
        sender_id="YOUR_EXISTING_SENDER_UUID",
        template_id="YOUR_EXISTING_TEMPLATE_UUID"
    )
    try:
        placeholder_provider.validate_configuration()
        assert_true(False, "Should reject placeholder credentials")
    except SMSConfigurationError:
        assert_true(True, "Properly rejected placeholder credentials")

    # 7. Mocked OTP.dev HTTP Call - Success (POST /v1/verifications)
    valid_provider = OTPDevSMSProvider(
        api_key="test_otpdev_key_xyz",
        sender_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        template_id="6d16aa9d-bf19-4141-8169-48b46d972fc6"
    )
    mock_success_response = json.dumps({
        "account_id": "acc_123",
        "message_id": "msg_otpdev_789",
        "phone": "+919876543210",
        "create_date": "2026-11-16T10:00:00.000Z",
        "expire_date": "2026-11-16T10:05:00.000Z"
    }).encode("utf-8")
    
    mock_resp_obj = MagicMock()
    mock_resp_obj.read.return_value = mock_success_response
    mock_resp_obj.__enter__.return_value = mock_resp_obj

    with patch("urllib.request.urlopen", return_value=mock_resp_obj) as mock_urlopen:
        result = valid_provider.send_otp("9876543210", "654321")
        assert_true(result["success"] is True and result["request_id"] == "msg_otpdev_789", "OTP.dev provider returns success payload with request_id")
        
        # Verify request structure
        called_req = mock_urlopen.call_args[0][0]
        assert_true(called_req.full_url == "https://api.otp.dev/v1/verifications", "Calls https://api.otp.dev/v1/verifications")
        assert_true(called_req.headers.get("X-otp-key") == "test_otpdev_key_xyz", "Header X-OTP-Key contains API Key")
        assert_true(called_req.headers.get("Content-type") == "application/json", "Header Content-Type is application/json")
        
        sent_body = json.loads(called_req.data.decode("utf-8"))
        assert_true("data" in sent_body, "Body contains root data object")
        data_block = sent_body["data"]
        assert_true(data_block["channel"] == "sms", "Channel is sms")
        assert_true(data_block["sender"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6", "Sender ID UUID matches")
        assert_true(data_block["template"] == "6d16aa9d-bf19-4141-8169-48b46d972fc6", "Template UUID matches")
        assert_true(data_block["phone"] == "+919876543210", "Phone formatted as E.164 (+91XXXXXXXXXX)")
        assert_true(data_block["code"] == "654321", "Code matches generated OTP")
        assert_true(data_block["code_length"] == 6, "Code length is 6")

    # 8. Mocked OTP.dev HTTP Call - 401 Unauthorized
    with patch("urllib.request.urlopen") as mock_urlopen:
        fp = MagicMock()
        fp.read.return_value = json.dumps({"type": "error", "message": "Unauthorized"}).encode("utf-8")
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.otp.dev/v1/verifications",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=fp
        )
        try:
            valid_provider.send_otp("9876543210", "654321")
            assert_true(False, "Should raise SMSGatewayError on 401")
        except SMSGatewayError as sge:
            assert_true("Authentication Failed" in str(sge), "Clear authentication failure message on 401")

    # 9. Mocked OTP.dev HTTP Call - 429 Rate Limit
    with patch("urllib.request.urlopen") as mock_urlopen:
        fp = MagicMock()
        fp.read.return_value = json.dumps({"type": "error", "message": "Rate limit exceeded"}).encode("utf-8")
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.otp.dev/v1/verifications",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=fp
        )
        try:
            valid_provider.send_otp("9876543210", "654321")
            assert_true(False, "Should raise SMSGatewayError on 429")
        except SMSGatewayError as sge:
            assert_true("Rate Limit" in str(sge), "Clear rate limit error on 429")

    # 10. Mocked OTP.dev Server-Side Verification (GET /v1/verifications?code=...&phone=...)
    # Case A: Valid code (data array non-empty)
    mock_verify_valid_response = json.dumps({
        "data": [{"message_id": "msg_otpdev_789", "phone": "+919876543210"}],
        "pagination": {"number": 1, "size": 1, "total": 1}
    }).encode("utf-8")
    mock_resp_valid = MagicMock()
    mock_resp_valid.read.return_value = mock_verify_valid_response
    mock_resp_valid.__enter__.return_value = mock_resp_valid

    with patch("urllib.request.urlopen", return_value=mock_resp_valid) as mock_urlopen:
        assert_true(valid_provider.verify_otp("9876543210", "654321") is True, "Online verification returns True when OTP.dev validates code")
        called_req = mock_urlopen.call_args[0][0]
        assert_true("code=654321" in called_req.full_url, "Query contains code parameter")
        assert_true("phone=%2B919876543210" in called_req.full_url or "phone=+919876543210" in called_req.full_url, "Query contains E.164 phone")
        assert_true(called_req.headers.get("X-otp-key") == "test_otpdev_key_xyz", "Header X-OTP-Key passed on verification GET")

    # Case B: Invalid or expired code (data array empty)
    mock_verify_invalid_response = json.dumps({
        "data": [],
        "pagination": {"number": 1, "size": 0, "total": 0}
    }).encode("utf-8")
    mock_resp_invalid = MagicMock()
    mock_resp_invalid.read.return_value = mock_verify_invalid_response
    mock_resp_invalid.__enter__.return_value = mock_resp_invalid

    with patch("urllib.request.urlopen", return_value=mock_resp_invalid):
        assert_true(valid_provider.verify_otp("9876543210", "000000") is False, "Online verification returns False when OTP.dev returns empty data array")

    # 11. Backend Live HTTP Endpoint behavior with missing/unconfigured credentials (503 Service Unavailable)
    unreg_phone = "9999900010"
    req = urllib.request.Request(
        "http://127.0.0.1:8000/auth/otp/send",
        data=json.dumps({"phone": unreg_phone, "purpose": "register"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        assert_true(False, "Live backend should return 503 when credentials missing")
    except urllib.error.HTTPError as he:
        err_body = he.read().decode("utf-8")
        err_data = json.loads(err_body)
        assert_true(he.code == 503, "Live endpoint returns HTTP 503 for unconfigured SMS provider")
        assert_true("OTPDEV_API_KEY" in err_data.get("detail", ""), "HTTP 503 detail specifies missing OTPDEV_API_KEY")
        assert_true("OTPDEV_SENDER_ID" in err_data.get("detail", ""), "HTTP 503 detail specifies missing OTPDEV_SENDER_ID")
        assert_true("OTPDEV_SMS_TEMPLATE_ID" in err_data.get("detail", ""), "HTTP 503 detail specifies missing OTPDEV_SMS_TEMPLATE_ID")

    # 12. End-to-end registration flow with direct endpoint function execution
    from main import send_otp, register_citizen_with_otp, login_citizen_with_otp, SendOtpRequest, RegisterWithOtpRequest, LoginWithOtpRequest
    from fastapi import HTTPException
    
    test_citizen_phone = "9999900012"
    
    # Clean up test records if any exist
    conn = sqlite3.connect("/app/data/nagriksetu.db")
    with conn:
        conn.execute("DELETE FROM phone_otps WHERE phone = ?", (test_citizen_phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (test_citizen_phone,))

    dummy_request = MagicMock()
    dummy_request.client.host = "127.0.0.1"

    # Patch send_otp_sms with mock OTP.dev success
    with patch("sms_service.send_otp_sms") as mock_send_sms:
        mock_send_sms.return_value = {
            "success": True,
            "provider": "otpdev",
            "request_id": "msg_otpdev_test_456",
            "message": "OTP dispatched successfully via OTP.dev SMS gateway."
        }
        
        # Test endpoint returns 200 and zero dev_otp / plain otp
        send_resp = send_otp(dummy_request, SendOtpRequest(phone=test_citizen_phone, purpose="register"))
        assert_true("dev_otp" not in send_resp, "Response JSON contains NO dev_otp field")
        assert_true("otp" not in send_resp, "Response JSON contains NO plain otp field")
        assert_true(send_resp.get("provider") == "otpdev", "Provider correctly identified as otpdev")

        # 13. Enforce 60-second cooldown on immediate re-send
        try:
            send_otp(dummy_request, SendOtpRequest(phone=test_citizen_phone, purpose="register"))
            assert_true(False, "Should reject immediate re-send within 60s cooldown")
        except HTTPException as cooldown_err:
            assert_true(cooldown_err.status_code == 429, "Immediate re-send returns HTTP 429 Too Many Requests")

        # Retrieve the OTP hash from DB and find the matched OTP to verify database hashing
        row = conn.execute("SELECT * FROM phone_otps WHERE phone = ? AND purpose = 'register' AND is_used = 0", (test_citizen_phone,)).fetchone()
        assert_true(row is not None, "OTP record saved to database after provider accepts")
        stored_hash = row[2] # otp_hash column
        otp_id = row[0]

        # Find the 6-digit code matching the test record hash
        matched_otp = None
        for cand in range(100000, 1000000):
            if verify_otp_hash(test_citizen_phone, str(cand), stored_hash):
                matched_otp = str(cand)
                break
        assert_true(matched_otp is not None, "Generated OTP in DB accurately verifies against hash")

        # 14. Test wrong OTP rejection & attempt counter decrement
        try:
            register_citizen_with_otp(RegisterWithOtpRequest(phone=test_citizen_phone, otp="000000", full_name="Test Citizen"))
            assert_true(False, "Should reject wrong OTP")
        except HTTPException as wrong_err:
            assert_true(wrong_err.status_code == 400, "Wrong OTP returns HTTP 400")
            assert_true("Incorrect OTP" in wrong_err.detail and "4 verification attempts remaining" in wrong_err.detail, "Informs remaining attempts correctly")

        # 15. Test 5 failed attempts locks OTP
        for attempt in range(4):
            try:
                register_citizen_with_otp(RegisterWithOtpRequest(phone=test_citizen_phone, otp="000000", full_name="Test Citizen"))
            except HTTPException:
                pass
        
        try:
            register_citizen_with_otp(RegisterWithOtpRequest(phone=test_citizen_phone, otp=matched_otp, full_name="Test Citizen"))
            assert_true(False, "Should reject OTP when max attempts exceeded")
        except HTTPException as lockout_err:
            assert_true(lockout_err.status_code == 400, "Exceeded attempts returns HTTP 400")
            assert_true("Too many invalid attempts" in lockout_err.detail, "Locked out after 5 failed attempts")

        # 16. Invalidation of older active OTPs upon new send
        # Backdate created_at of existing OTPs so 60-second cooldown allows new dispatch
        with conn:
            conn.execute("UPDATE phone_otps SET created_at = '2020-01-01 00:00:00' WHERE phone = ?", (test_citizen_phone,))
        
        send_resp_2 = send_otp(dummy_request, SendOtpRequest(phone=test_citizen_phone, purpose="register"))
        row2 = conn.execute("SELECT * FROM phone_otps WHERE phone = ? AND purpose = 'register' AND is_used = 0", (test_citizen_phone,)).fetchall()
        assert_true(len(row2) == 1, "Only one active OTP exists after new dispatch; older OTPs invalidated")
        
        new_stored_hash = row2[0][2]
        new_matched_otp = None
        for cand in range(100000, 1000000):
            if verify_otp_hash(test_citizen_phone, str(cand), new_stored_hash):
                new_matched_otp = str(cand)
                break

        # 17. Expired OTP rejection
        with conn:
            conn.execute("UPDATE phone_otps SET expires_at = '2020-01-01 00:00:00' WHERE otp_id = ?", (row2[0][0],))
        try:
            register_citizen_with_otp(RegisterWithOtpRequest(phone=test_citizen_phone, otp=new_matched_otp, full_name="Test Citizen"))
            assert_true(False, "Should reject expired OTP")
        except HTTPException as exp_err:
            assert_true(exp_err.status_code == 400, "Expired OTP returns HTTP 400")
            assert_true("expired" in exp_err.detail.lower(), "Expired OTP error message detail")

        # 18. Successful registration with fresh valid OTP
        with conn:
            conn.execute("UPDATE phone_otps SET created_at = '2020-01-01 00:00:00' WHERE phone = ?", (test_citizen_phone,))
        
        send_resp_3 = send_otp(dummy_request, SendOtpRequest(phone=test_citizen_phone, purpose="register"))
        row3 = conn.execute("SELECT * FROM phone_otps WHERE phone = ? AND purpose = 'register' AND is_used = 0", (test_citizen_phone,)).fetchone()
        fresh_hash = row3[2]
        fresh_otp = None
        for cand in range(100000, 1000000):
            if verify_otp_hash(test_citizen_phone, str(cand), fresh_hash):
                fresh_otp = str(cand)
                break

        reg_resp = register_citizen_with_otp(RegisterWithOtpRequest(phone=test_citizen_phone, otp=fresh_otp, full_name="Test Citizen"))
        assert_true("access_token" in reg_resp, "Issues JWT access token")
        assert_true(reg_resp.get("role") == "parent", "Assigns citizen/parent role")

        # 19. Replay protection - Reused OTP rejection
        try:
            register_citizen_with_otp(RegisterWithOtpRequest(phone=test_citizen_phone, otp=fresh_otp, full_name="Test Citizen"))
            assert_true(False, "Should reject already used OTP")
        except HTTPException as replay_err:
            assert_true(replay_err.status_code in (400, 409), "Replay with used OTP rejected")

    # Clean up test user
    with conn:
        conn.execute("DELETE FROM phone_otps WHERE phone = ?", (test_citizen_phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (test_citizen_phone,))
    conn.close()

    print("\n--------------------------------------------------")
    print(f"RESULTS: {passed} PASSED, {failed} FAILED")
    print("--------------------------------------------------")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
