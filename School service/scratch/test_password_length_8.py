import requests
import uuid
import sqlite3

base_url = "http://localhost:8001"
db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

print("==================================================================")
print("TESTING 8-CHARACTER PASSWORD MINIMUM VALIDATION & COMPLIANCE")
print("==================================================================")

# -----------------------------------------------------------------------------
# 1. Parent Registration Length Testing
# -----------------------------------------------------------------------------
# A. 7-character password -> MUST BE REJECTED (HTTP 422)
phone_7 = f"98{uuid.uuid4().int % 89999999 + 10000000}"
res_p7 = requests.post(
    f"{base_url}/auth/register",
    json={
        "full_name": "Test Parent Seven",
        "phone": phone_7,
        "password": "Pass12!",  # 7 chars
        "confirm_password": "Pass12!"
    }
)
assert res_p7.status_code == 422, f"Expected 422 for 7-char password, got {res_p7.status_code}: {res_p7.text}"
print("1. Parent Registration: 7-character password rejected (HTTP 422): PASSED")

# B. 8-character password -> MUST BE ACCEPTED (HTTP 200)
phone_8 = f"98{uuid.uuid4().int % 89999999 + 10000000}"
res_p8 = requests.post(
    f"{base_url}/auth/register",
    json={
        "full_name": "Test Parent Eight",
        "phone": phone_8,
        "password": "Pass8ch!",  # 8 chars
        "confirm_password": "Pass8ch!"
    }
)
assert res_p8.status_code == 201, f"Expected 200 for 8-char password, got {res_p8.status_code}: {res_p8.text}"
print("2. Parent Registration: 8-character password accepted: PASSED")

# Verify login with 8-character password
res_p8_login = requests.post(
    f"{base_url}/auth/login",
    data={"username": phone_8, "password": "Pass8ch!"}
)
assert res_p8_login.status_code == 200, f"Login with 8-char password failed: {res_p8_login.text}"
print("3. Parent Login with 8-character password: PASSED")

# C. 10-character password -> ACCEPTED
phone_10 = f"98{uuid.uuid4().int % 89999999 + 10000000}"
res_p10 = requests.post(
    f"{base_url}/auth/register",
    json={
        "full_name": "Test Parent Ten",
        "phone": phone_10,
        "password": "PassTen123",  # 10 chars
        "confirm_password": "PassTen123"
    }
)
assert res_p10.status_code == 201
print("4. Parent Registration: 10-character password accepted: PASSED")

# D. 11-character password -> ACCEPTED
phone_11 = f"98{uuid.uuid4().int % 89999999 + 10000000}"
res_p11 = requests.post(
    f"{base_url}/auth/register",
    json={
        "full_name": "Test Parent Eleven",
        "phone": phone_11,
        "password": "Pass11Chars",  # 11 chars
        "confirm_password": "Pass11Chars"
    }
)
assert res_p11.status_code == 201
print("5. Parent Registration: 11-character password accepted: PASSED")

# E. 12-character password -> ACCEPTED
phone_12 = f"98{uuid.uuid4().int % 89999999 + 10000000}"
res_p12 = requests.post(
    f"{base_url}/auth/register",
    json={
        "full_name": "Test Parent Twelve",
        "phone": phone_12,
        "password": "Pass12Chars!",  # 12 chars
        "confirm_password": "Pass12Chars!"
    }
)
assert res_p12.status_code == 201
print("6. Parent Registration: 12-character password accepted: PASSED")


# -----------------------------------------------------------------------------
# 2. Institution Admin Invitation Acceptance Length Testing
# -----------------------------------------------------------------------------
# Login platform admin to invite institution admin
res_pa = requests.post(
    f"{base_url}/auth/login",
    data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"}
)
pa_token = res_pa.json()["access_token"]
pa_headers = {"Authorization": f"Bearer {pa_token}"}

# Invite admin
adm_email = f"testadmin.{uuid.uuid4().hex[:4]}@example.com"
res_inv_adm = requests.post(
    f"{base_url}/admin/institution-admins/invite",
    headers=pa_headers,
    json={
        "full_name": "Admin Eight Test",
        "email": adm_email,
        "institution_id": "SCH001",
        "role_id": "school_admin"
    }
)
inv_token = res_inv_adm.json()["invitation_token"]

# A. Try accepting with 7 characters -> REJECTED (HTTP 422)
res_adm_7 = requests.post(
    f"{base_url}/auth/accept-invitation",
    json={"token": inv_token, "password": "Admin7!"}  # 7 chars
)
assert res_adm_7.status_code == 422, f"Expected 422, got {res_adm_7.status_code}: {res_adm_7.text}"
print("7. Institution Admin: 7-character password rejected (HTTP 422): PASSED")

# B. Accept with 8 characters -> ACCEPTED (HTTP 200)
res_adm_8 = requests.post(
    f"{base_url}/auth/accept-invitation",
    json={"token": inv_token, "password": "Adm8Pass"}  # 8 chars
)
assert res_adm_8.status_code == 200, f"Expected 200, got {res_adm_8.status_code}: {res_adm_8.text}"
print("8. Institution Admin: 8-character password accepted: PASSED")

# Verify login with 8-character password
res_adm_login = requests.post(
    f"{base_url}/auth/login?institution_id=SCH001",
    data={"username": adm_email, "password": "Adm8Pass"}
)
assert res_adm_login.status_code == 200
print("9. Institution Admin Login with 8-character password: PASSED")


# -----------------------------------------------------------------------------
# 3. Staff Candidate Account Activation Length Testing
# -----------------------------------------------------------------------------
# Login SCH019 Admin
res_sch019 = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "admin.sch019@gmail.com", "password": "Admin@NagrikSetu2026!"}
)
sch019_headers = {"Authorization": f"Bearer {res_sch019.json()['access_token']}"}

cand_email = f"staff.eight.{uuid.uuid4().hex[:4]}@example.com"
res_cand_inv = requests.post(
    f"{base_url}/school/admin/staff-applications/invite",
    headers=sch019_headers,
    json={
        "candidate_name": "Radha Sharma",
        "candidate_email": cand_email,
        "role_id": "admissions_officer",
        "institution_id": "SCH019"
    }
)
cand_tok = res_cand_inv.json()["candidate_token"]
cand_app_id = res_cand_inv.json()["application_id"]

# Candidate submits
requests.post(
    f"{base_url}/auth/staff-candidate/submit",
    json={"token": cand_tok, "qualifications": [{"degree": "B.Com", "year": "2020"}]}
)

# Admin approves
res_appr = requests.post(
    f"{base_url}/school/admin/staff-applications/{cand_app_id}/approve",
    headers=sch019_headers,
    json={"review_notes": "Approved."}
)
act_token = res_appr.json()["activation_token"]

# A. 7-character activation password -> REJECTED (HTTP 422)
res_act_7 = requests.post(
    f"{base_url}/auth/staff-candidate/activate",
    json={"activation_token": act_token, "password": "Staff7!"}  # 7 chars
)
assert res_act_7.status_code == 422, f"Expected 422, got {res_act_7.status_code}: {res_act_7.text}"
print("10. Staff Candidate Activation: 7-character password rejected (HTTP 422): PASSED")

# B. 8-character activation password -> ACCEPTED (HTTP 200)
res_act_8 = requests.post(
    f"{base_url}/auth/staff-candidate/activate",
    json={"activation_token": act_token, "password": "Staff8Ch"}  # 8 chars
)
assert res_act_8.status_code == 200, f"Expected 200, got {res_act_8.status_code}: {res_act_8.text}"
print("11. Staff Candidate Activation: 8-character password accepted: PASSED")

# Verify login with 8-character password
res_staff_login = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": cand_email, "password": "Staff8Ch"}
)
assert res_staff_login.status_code == 200
print("12. Staff Login with 8-character password: PASSED")


# -----------------------------------------------------------------------------
# 4. Password Reset Length Testing
# -----------------------------------------------------------------------------
# Request password reset for a parent
reset_phone = phone_8
res_fp = requests.post(
    f"{base_url}/auth/forgot-password",
    json={"identifier": reset_phone}
)
assert res_fp.status_code == 200
reset_token = res_fp.json()["reset_token"]

# A. 7-character reset password -> REJECTED (HTTP 422)
res_rst_7 = requests.post(
    f"{base_url}/auth/reset-password",
    json={"token": reset_token, "new_password": "New7Ch!"}  # 7 chars
)
assert res_rst_7.status_code == 422, f"Expected 422, got {res_rst_7.status_code}: {res_rst_7.text}"
print("13. Password Reset: 7-character password rejected (HTTP 422): PASSED")

# B. 8-character reset password -> ACCEPTED (HTTP 200)
res_rst_8 = requests.post(
    f"{base_url}/auth/reset-password",
    json={"token": reset_token, "new_password": "New8Char"}  # 8 chars
)
assert res_rst_8.status_code == 200, f"Expected 200, got {res_rst_8.status_code}: {res_rst_8.text}"
print("14. Password Reset: 8-character password accepted: PASSED")

# Verify login with reset 8-character password
res_rst_login = requests.post(
    f"{base_url}/auth/login",
    data={"username": reset_phone, "password": "New8Char"}
)
assert res_rst_login.status_code == 200
print("15. Login with newly reset 8-character password: PASSED")


# -----------------------------------------------------------------------------
# 5. Change Password Length Testing (Authenticated User)
# -----------------------------------------------------------------------------
parent_token = res_rst_login.json()["access_token"]
p_headers = {"Authorization": f"Bearer {parent_token}"}

# A. 7-character change password -> REJECTED (HTTP 422)
res_cp_7 = requests.post(
    f"{base_url}/auth/change-password",
    headers=p_headers,
    json={"old_password": "New8Char", "new_password": "Chg7Ch!"}
)
assert res_cp_7.status_code == 422
print("16. Change Password: 7-character password rejected (HTTP 422): PASSED")

# B. 8-character change password -> ACCEPTED (HTTP 200)
res_cp_8 = requests.post(
    f"{base_url}/auth/change-password",
    headers=p_headers,
    json={"old_password": "New8Char", "new_password": "Chg8Char"}
)
assert res_cp_8.status_code == 200
print("17. Change Password: 8-character password accepted: PASSED")

# Verify login with changed password
res_cp_login = requests.post(
    f"{base_url}/auth/login",
    data={"username": reset_phone, "password": "Chg8Char"}
)
assert res_cp_login.status_code == 200
print("18. Login with changed 8-character password: PASSED")


# -----------------------------------------------------------------------------
# 6. Existing Account Logins Regression (Must Still Work Intact!)
# -----------------------------------------------------------------------------
# A. Existing Parent Account
res_exist_p = requests.post(
    f"{base_url}/auth/login",
    data={"username": "9876543210", "password": "Str0ngPass!2026"}
)
assert res_exist_p.status_code == 200, f"Existing parent login failed: {res_exist_p.text}"
assert res_exist_p.json()["role"] == "parent"
print("19. Regression: Existing Parent login (9876543210): PASSED")

# B. Existing Platform Admin Account
res_exist_pa = requests.post(
    f"{base_url}/auth/login",
    data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"}
)
assert res_exist_pa.status_code == 200, f"Existing Platform Admin login failed: {res_exist_pa.text}"
assert res_exist_pa.json()["role"] == "platform_admin"
print("20. Regression: Existing Platform Admin login (admin.central@nagriksetu.gov): PASSED")

# C. Existing Institution Admin Account (SCH019)
res_exist_ia = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "admin.sch019@gmail.com", "password": "Admin@NagrikSetu2026!"}
)
assert res_exist_ia.status_code == 200, f"Existing SCH019 Admin login failed: {res_exist_ia.text}"
assert res_exist_ia.json()["role"] == "school_admin"
print("21. Regression: Existing SCH019 Admin login: PASSED")

# D. Existing Institution Staff Account (Admissions Officer)
res_exist_st = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "test.admissions.sch019@example.com", "password": "Password@1234567!"}
)
assert res_exist_st.status_code == 200, f"Existing Staff login failed: {res_exist_st.text}"
assert res_exist_st.json()["role"] == "admissions_officer"
print("22. Regression: Existing SCH019 Staff login: PASSED")


# -----------------------------------------------------------------------------
# 7. Database Integrity & Argon2id Hashing Verification
# -----------------------------------------------------------------------------
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check that passwords are stored as Argon2id hashes and NOT plaintext
cur.execute("SELECT password_hash FROM users WHERE phone = ?", (phone_8,))
h = cur.fetchone()[0]
assert h.startswith("$argon2id$"), f"Expected Argon2id hash, got: {h}"
assert "Pass8ch!" not in h, "Plaintext password detected in database!"
print("23. Security: Password confirmed hashed with Argon2id ($argon2id$), no plaintext stored: PASSED")

# PRAGMA integrity_check
cur.execute("PRAGMA integrity_check")
ic = cur.fetchall()
assert ic == [("ok",)], f"Integrity check failed: {ic}"
print("24. Database: PRAGMA integrity_check ok: PASSED")

# PRAGMA foreign_key_check
cur.execute("PRAGMA foreign_key_check")
fk = cur.fetchall()
assert fk == [], f"Foreign key violations found: {fk}"
print("25. Database: PRAGMA foreign_key_check 0 violations: PASSED")

# Count active institutions
cur.execute("SELECT COUNT(*) FROM schools")
assert cur.fetchone()[0] == 30
print("26. Database: Exactly 30 institutions preserved: PASSED")

# Count students
cur.execute("SELECT COUNT(*) FROM students")
assert cur.fetchone()[0] == 30001
print("27. Database: Exactly 30,001 students preserved: PASSED")

# Count enrollments
cur.execute("SELECT COUNT(*) FROM enrollments")
assert cur.fetchone()[0] == 30001
print("28. Database: Exactly 30,001 enrollments preserved: PASSED")

# Count admission applications
cur.execute("SELECT COUNT(*) FROM admission_applications")
assert cur.fetchone()[0] == 57
print("29. Database: Exactly 57 admission applications preserved: PASSED")

conn.close()

print("==================================================================")
print("ALL 29/29 PASSWORD VALIDATION & REGRESSION TESTS PASSED!")
print("==================================================================")
