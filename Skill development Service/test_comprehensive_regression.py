import requests
import json
import time

BASE_URL = "http://127.0.0.1:8003"
FRONTEND_GATEWAY = "http://127.0.0.1:5178"

# 10 Accredited Centres with freshly rotated unique passwords (Argon2id)
CENTRES = [
    (1, "centre.bengaluru@nagriksetu.local", "BengaluruHub#2026", "Bengaluru Central Skill Hub (Rajajinagar)"),
    (2, "centre.admin.mysuru@nagriksetu.local", "MysuruSkill#2026", "Mysuru Regional Skilling Institute"),
    (3, "centre.admin.hubballi@nagriksetu.local", "HubballiTech#2026", "Hubballi-Dharwad Tech Development Centre"),
    (4, "centre.admin.mangaluru@nagriksetu.local", "MangaluruSea#2026", "Mangaluru Coastal Skill Academy"),
    (5, "centre.virtual@nagriksetu.local", "VirtualLearn#2026", "NagrikSetu Virtual Learning Portal"),
    (6, "centre.dharwad@nagriksetu.local", "DharwadInno#2026", "Dharwad Innovation & Regional Skilling Centre"),
    (8, "centre.belagavi@nagriksetu.local", "BelagaviHub#2026", "Belagavi Regional Skilling Hub"),
    (9, "centre.davanagere@nagriksetu.local", "DavanagereVoc#2026", "Davanagere Vocational & Technical Institute"),
    (10, "centre.kalaburagi@nagriksetu.local", "KalaburagiDev#2026", "Kalaburagi Regional Skill Development Centre"),
    (11, "centre.shivamogga@nagriksetu.local", "ShivamoggaMal#2026", "Shivamogga Malnad Skill Development Centre"),
]

ROTATED_OWNER_KEY = "NagrikSetu#OwnerAuth2026$Rotated9x!"
OLD_EXPOSED_KEYS = ["NagrikSetu@OwnerSecureKey2026!", "CentreAdmin@2026!", "demo_key"]

def run_comprehensive_verification():
    print("=" * 75)
    print("NAGRIKSETU FINAL REGRESSION & SECURITY VERIFICATION SUITE")
    print("=" * 75)
    results = {}

    # Check 1: Frontend Gateway
    r_fe = requests.get(f"{FRONTEND_GATEWAY}/")
    print(f"1. Frontend Delivery (Gateway 5178): HTTP {r_fe.status_code}")
    results["frontend_gateway"] = (r_fe.status_code == 200)

    # Check 2: Public Centre Register Data Masking
    r_pub = requests.get(f"{BASE_URL}/api/public/centre-register")
    pub_data = r_pub.json()
    all_masked = all(item.get("is_masked") is True for item in pub_data)
    print(f"2. Public Register Masking: HTTP {r_pub.status_code} | Total: {len(pub_data)} | All Masked: {all_masked}")
    results["public_register_masked"] = all_masked and (r_pub.status_code == 200) and (len(pub_data) == 10)

    # Check 3: Project Owner Authentication with Rotated Key & Rejection of Old Keys
    for old_k in OLD_EXPOSED_KEYS:
        r_old = requests.post(f"{BASE_URL}/api/auth/project-owner-login", json={"owner_key": old_k})
        assert r_old.status_code in (401, 429), f"Old key {old_k} should be rejected!"
    print(f"3a. Old Exposed Keys Invalidation: All rejected (HTTP 401)")

    r_good = requests.post(f"{BASE_URL}/api/auth/project-owner-login", json={"owner_key": ROTATED_OWNER_KEY})
    owner_token = r_good.json().get("access_token")
    print(f"3b. Rotated Project Owner Key Auth: HTTP {r_good.status_code} | Token Issued: {bool(owner_token)}")
    results["project_owner_auth"] = (r_good.status_code == 200) and bool(owner_token)

    # Check 4: Unmasked Register with Project Owner Bearer Token
    r_unmasked = requests.get(f"{BASE_URL}/api/public/centre-register", headers={"Authorization": f"Bearer {owner_token}"})
    unmasked_data = r_unmasked.json()
    all_unmasked = all(item.get("is_masked") is False for item in unmasked_data)
    print(f"4. Authenticated Unmasked Register: HTTP {r_unmasked.status_code} | Unmasked: {all_unmasked}")
    results["authenticated_unmasking"] = all_unmasked and (r_unmasked.status_code == 200)

    # Check 5: Project Owner Password Reset Endpoint Auth Requirement (Static key in body MUST FAIL)
    r_no_bearer = requests.post(
        f"{BASE_URL}/api/auth/project-owner-reset-centre-password",
        json={"centre_id": 1, "secret_key": ROTATED_OWNER_KEY, "new_password": "NewTestPassword123!"}
    )
    print(f"5a. Reset Without Bearer Token (Body Key Only): HTTP {r_no_bearer.status_code} (Exp 403 Forbidden)")
    results["reset_requires_bearer"] = (r_no_bearer.status_code == 403)

    # Check 6: Platform Admin Strictly Read-Only (HTTP 403 on write endpoints)
    admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "skill.admin@nagriksetu.local", "password": "SkillAdmin@2026!"})
    admin_token = admin_login.json().get("access_token")
    admin_assign = requests.post(
        f"{BASE_URL}/api/admin/centres/1/assign-admin",
        json={"email": "rep@test.local", "password": "Password123!", "full_name": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_review = requests.patch(
        f"{BASE_URL}/api/admin/enrollments/1/review",
        json={"status": "APPROVED", "remarks": "Review by Platform Admin"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_view = requests.get(f"{BASE_URL}/api/admin/centres", headers={"Authorization": f"Bearer {admin_token}"})
    print(f"6. Platform Admin Permissions: Assign Admin HTTP {admin_assign.status_code} (Exp 403) | Review Enrolment HTTP {admin_review.status_code} (Exp 403) | View Centres HTTP {admin_view.status_code} (Exp 200)")
    results["admin_read_only"] = (admin_assign.status_code == 403) and (admin_review.status_code == 403) and (admin_view.status_code == 200)

    # Check 7: All 10 Centre Logins with Rotated Passwords, Dashboard Access & Old Shared Password Rejection
    print("\n7. Testing All 10 Training Centre Logins & Isolation:")
    centre_status_list = []
    for cid, email, pwd, name in CENTRES:
        # Unique login
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": pwd})
        login_ok = (login_res.status_code == 200)
        token = login_res.json().get("access_token") if login_ok else None

        # Old shared password MUST FAIL
        old_res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": "CentreAdmin@2026!"})
        old_rejected = (old_res.status_code == 401)

        # Dashboard & App isolation
        dash_ok = False
        app_cnt = 0
        if token:
            dash_res = requests.get(f"{BASE_URL}/api/centre-admin/dashboard", headers={"Authorization": f"Bearer {token}"})
            dash_ok = (dash_res.status_code == 200)
            app_res = requests.get(f"{BASE_URL}/api/centre-admin/enrollments", headers={"Authorization": f"Bearer {token}"})
            if app_res.status_code == 200:
                app_cnt = len(app_res.json())

        status_line = f"Centre {cid:2d} | Login: {'PASS' if login_ok else 'FAIL'} | Shared Pwd Rejected: {'PASS' if old_rejected else 'FAIL'} | Dash: {'PASS' if dash_ok else 'FAIL'} | Apps: {app_cnt:2d} | {name}"
        print(f"   {status_line}")
        centre_status_list.append(login_ok and old_rejected and dash_ok)

    results["all_10_centres"] = all(centre_status_list)

    # Check 8: Representative Independent Password Change (/api/auth/change-password)
    # Test on Centre 11 (Shivamogga)
    c11_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "centre.shivamogga@nagriksetu.local", "password": "ShivamoggaMal#2026"})
    c11_token = c11_login.json().get("access_token")
    temp_pwd = "Shv#NewPass2026Updated!"
    # Change password
    r_chg = requests.post(
        f"{BASE_URL}/api/auth/change-password",
        json={"current_password": "ShivamoggaMal#2026", "new_password": temp_pwd, "confirm_password": temp_pwd},
        headers={"Authorization": f"Bearer {c11_token}"}
    )
    # Verify new password login
    r_verify_new = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "centre.shivamogga@nagriksetu.local", "password": temp_pwd})
    # Restore back to original permanent password
    if r_verify_new.status_code == 200:
        c11_new_token = r_verify_new.json().get("access_token")
        requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={"current_password": temp_pwd, "new_password": "ShivamoggaMal#2026", "confirm_password": "ShivamoggaMal#2026"},
            headers={"Authorization": f"Bearer {c11_new_token}"}
        )
    print(f"\n8. Centre Representative Independent Password Change: Change HTTP {r_chg.status_code} | New Pwd Login HTTP {r_verify_new.status_code}")
    results["representative_password_change"] = (r_chg.status_code == 200) and (r_verify_new.status_code == 200)

    # Check 9: Citizen SMTP OTP Login Configuration & Application Submission
    r_otp_status = requests.get(f"{BASE_URL}/api/otp/status")
    otp_data = r_otp_status.json()
    print(f"9a. Citizen OTP System: Provider '{otp_data.get('provider')}' | Configured: {otp_data.get('configured')} | Demo Mode: {otp_data.get('demo_mode')}")
    results["citizen_smtp_configured"] = (otp_data.get("configured") is True) and (otp_data.get("demo_mode") is False)

    # Check 10: Security Audit Log Persistence in MySQL
    r_audit = requests.get(f"{BASE_URL}/api/admin/audit", headers={"Authorization": f"Bearer {admin_token}"})
    audit_data = r_audit.json()
    print(f"10. MySQL Audit Logs: HTTP {r_audit.status_code} | Total Recorded Events: {len(audit_data)}")
    results["audit_logs"] = (r_audit.status_code == 200) and (len(audit_data) > 0)

    print("\n" + "=" * 75)
    overall_pass = all(results.values())
    print("FINAL RESULT:", "ALL SECURITY REGRESSION CHECKS PASSED (100%)" if overall_pass else "CHECKS FAILED")
    print("=" * 75)

    with open("final_security_regression_results.json", "w", encoding="utf-8") as f:
        json.dump({"overall_pass": overall_pass, "details": results}, f, indent=2)

if __name__ == "__main__":
    run_comprehensive_verification()
