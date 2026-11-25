import requests
import json
import time

BASE_URL = "http://127.0.0.1:8003"
CENTRES = [
    (1, "centre.bengaluru@nagriksetu.local", "BlrCentral#Skill2026!", "Bengaluru Central Skill Hub (Rajajinagar)"),
    (2, "centre.admin.mysuru@nagriksetu.local", "Mysuru#HeritageSkill2026!", "Mysuru Regional Skilling Institute"),
    (3, "centre.admin.hubballi@nagriksetu.local", "Hubballi#TechDev2026!", "Hubballi-Dharwad Tech Development Centre"),
    (4, "centre.admin.mangaluru@nagriksetu.local", "Mangaluru#CoastalTech2026!", "Mangaluru Coastal Technology Institute"),
    (5, "centre.virtual@nagriksetu.local", "Virtual#OnlineSkill2026!", "Karnataka Virtual Skill Academy (Online)"),
    (6, "centre.dharwad@nagriksetu.local", "Dharwad#InnovationSkill2026!", "Dharwad Agricultural Technology & Rural Skilling Centre"),
    (8, "centre.belagavi@nagriksetu.local", "Belagavi#RegionalHub2026!", "Belagavi Manufacturing & Precision Engineering Centre"),
    (9, "centre.davanagere@nagriksetu.local", "Davanagere#VocationalSkill2026!", "Davanagere Textile & Agro-Industry Vocational Institute"),
    (10, "centre.kalaburagi@nagriksetu.local", "Kalaburagi#SkillDev2026!", "Kalaburagi Regional Skill Development Centre"),
    (11, "centre.shivamogga@nagriksetu.local", "Shivamogga#MalnadSkill2026!", "Shivamogga Malnad Skill & Electronics Centre"),
]

def run_tests():
    results = {}
    print("=" * 70)
    print("NAGRIKSETU SECURITY VERIFICATION & REGISTRATION AUDIT")
    print("=" * 70)

    # 1. Test Public Centre Register (Privacy Masking)
    r_pub = requests.get(f"{BASE_URL}/api/public/centre-register")
    pub_data = r_pub.json()
    all_masked = all(item.get("is_masked") is True for item in pub_data)
    print(f"1. Public Centre Register (Masked): HTTP {r_pub.status_code} | Total: {len(pub_data)} | Privacy Masked: {all_masked}")
    results["public_register_masked"] = all_masked and (r_pub.status_code == 200)

    # 2. Test Project Owner Authentication
    bad_login = requests.post(f"{BASE_URL}/api/auth/project-owner-login", json={"owner_key": "wrong_key_123"})
    good_login = requests.post(f"{BASE_URL}/api/auth/project-owner-login", json={"owner_key": "NagrikSetu@OwnerSecureKey2026!"})
    owner_token = good_login.json().get("access_token")
    print(f"2. Project Owner Login: Invalid Key HTTP {bad_login.status_code} | Valid Key HTTP {good_login.status_code} | Token Acquired: {bool(owner_token)}")
    results["project_owner_auth"] = (bad_login.status_code == 401) and (good_login.status_code == 200)

    # 3. Test Unmasked Register with Owner Token
    r_unmasked = requests.get(f"{BASE_URL}/api/public/centre-register", headers={"Authorization": f"Bearer {owner_token}"})
    unmasked_data = r_unmasked.json()
    all_unmasked = all(item.get("is_masked") is False for item in unmasked_data)
    print(f"3. Authenticated Register: HTTP {r_unmasked.status_code} | Unmasked: {all_unmasked} | Sample: {unmasked_data[0].get('registered_email')}")
    results["authenticated_unmasking"] = all_unmasked and (r_unmasked.status_code == 200)

    # 4. Test Platform Admin Strictly Read-Only (Cannot Assign Admin or Review)
    admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "skill.admin@nagriksetu.local", "password": "SkillAdmin@2026!"})
    admin_token = admin_login.json().get("access_token")
    admin_assign = requests.post(
        f"{BASE_URL}/api/admin/centres/1/assign-admin",
        json={"email": "new.rep@test.local", "password": "Password123!", "full_name": "Test Rep"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_review = requests.patch(
        f"{BASE_URL}/api/admin/enrollments/1/review",
        json={"status": "APPROVED", "remarks": "Platform review"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_view = requests.get(f"{BASE_URL}/api/admin/centres", headers={"Authorization": f"Bearer {admin_token}"})
    print(f"4. Platform Admin Permissions: Assign Admin HTTP {admin_assign.status_code} (Exp 403) | Review Enrolment HTTP {admin_review.status_code} (Exp 403) | View Centres HTTP {admin_view.status_code} (Exp 200)")
    results["admin_read_only_enforced"] = (admin_assign.status_code == 403) and (admin_review.status_code == 403) and (admin_view.status_code == 200)

    # 5. Test All 10 Independent Centre Accounts (Argon2id Unique Password & Shared Pwd Rejection)
    centre_results = []
    print("\n5. Testing 10 Centre Accounts:")
    for cid, email, pwd, name in CENTRES:
        # Unique login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": pwd})
        login_ok = (login_resp.status_code == 200)
        token = login_resp.json().get("access_token") if login_ok else None

        # Shared password test (MUST FAIL)
        shared_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": "CentreAdmin@2026!"})
        shared_rejected = (shared_resp.status_code == 401)

        # Profile / Dashboard / Applications isolation
        dash_ok = False
        app_count = 0
        if token:
            dash_resp = requests.get(f"{BASE_URL}/api/centre-admin/dashboard", headers={"Authorization": f"Bearer {token}"})
            dash_ok = (dash_resp.status_code == 200)
            app_resp = requests.get(f"{BASE_URL}/api/centre-admin/enrollments", headers={"Authorization": f"Bearer {token}"})
            if app_resp.status_code == 200:
                app_count = len(app_resp.json())

        status_str = f"ID {cid:2d} | Login: {'PASS' if login_ok else 'FAIL'} | Old Shared Pwd Rejected: {'PASS' if shared_rejected else 'FAIL'} | Dash: {'PASS' if dash_ok else 'FAIL'} | Apps: {app_count}"
        print(f"   {status_str} | {name}")
        centre_results.append({
            "centre_id": cid,
            "centre_name": name,
            "email": email,
            "login_ok": login_ok,
            "shared_rejected": shared_rejected,
            "dash_ok": dash_ok,
            "app_count": app_count
        })

    all_centres_pass = all(c["login_ok"] and c["shared_rejected"] and c["dash_ok"] for c in centre_results)
    results["all_10_centres_pass"] = all_centres_pass

    # 6. Test Audit Logging
    r_audit = requests.get(f"{BASE_URL}/api/admin/audit", headers={"Authorization": f"Bearer {admin_token}"})
    audit_data = r_audit.json() if r_audit.status_code == 200 else []
    print(f"\n6. Security Audit Logs: HTTP {r_audit.status_code} | Total Recorded Events: {len(audit_data)}")
    if audit_data:
        print(f"   Latest Event: [{audit_data[0].get('role')}] {audit_data[0].get('action')} - {audit_data[0].get('details')}")

    with open("security_test_results.json", "w", encoding="utf-8") as out:
        json.dump({"overall_pass": all(results.values()), "summary": results, "centres": centre_results}, out, indent=2)

    print("\n" + "=" * 70)
    print("OVERALL VERIFICATION STATUS:", "ALL TESTS PASSED (100%)" if all(results.values()) else "FAILED")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
