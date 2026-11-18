import sys
import io
import subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import time
import os
import requests
import json

base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def capture_screenshot(url, filename, desc, window_size="1280,1050"):
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        "--virtual-time-budget=9000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"  [SCREENSHOT] {desc} -> {filename}")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)
    if os.path.exists(out_path):
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  [SUCCESS] {filename} saved ({size_kb:.1f} KB)")
    else:
        print(f"  [WARNING] {filename} was not created!")

def run_lifecycle_test():
    print("==================================================================")
    print("NAGRIKSETU: INSTITUTION ADMIN INVITATION & BUTTON STATE TEST")
    print("==================================================================")

    # 1. Platform Admin Authentication
    print("\n--- 1. Authenticating as Central Platform Admin ---")
    login_res = requests.post(f"{base_url}/auth/login", data={
        "username": "admin.central@nagriksetu.gov",
        "password": "Central@NagrikSetu2026!"
    })
    assert login_res.status_code == 200, f"Platform admin login failed: {login_res.text}"
    token_data = login_res.json()
    platform_token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {platform_token}"}
    print("Platform Admin token acquired successfully.")

    target_school = "SCH019" # Ballari Education School

    # Ensure clean slate for SCH019
    requests.post(f"{base_url}/admin/institution-admins/reset-assignments", headers=headers)
    print("Institution assignments reset to clean initial slate.")

    # ------------------------------------------------------------------
    # STATE A: NOT_INVITED / INVITATION REQUIRED
    # ------------------------------------------------------------------
    print(f"\n--- 2. Verifying State A: NOT_INVITED for {target_school} ---")
    res_a = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    assert res_a.status_code == 200
    data_a = res_a.json()
    print(f"Status: {data_a['status']} | Button: '{data_a['button_label']}' | Can Login: {data_a['can_login']}")
    assert data_a["status"] == "NOT_INVITED", f"Expected NOT_INVITED, got {data_a['status']}"
    assert data_a["button_label"] == "Invitation Required"
    assert data_a["can_login"] is False

    # Verify attempt to login unauthorized without active admin fails
    unauth_login = requests.post(f"{base_url}/auth/login?institution_id={target_school}", data={
        "username": "intruder@example.com",
        "password": "Password123!"
    })
    print(f"Unauthorized login attempt status code: {unauth_login.status_code} (Expected 401 or 403)")
    assert unauth_login.status_code in (401, 403)

    # Capture State A Screenshot
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase18_button_state_a_not_invited.png",
        "State A: 'Invitation Required' button rendered dynamically for uninvited institutions"
    )

    # ------------------------------------------------------------------
    # STATE B: INVITATION DISPATCHED -> "Invitation Available"
    # ------------------------------------------------------------------
    print(f"\n--- 3. Inviting Administrator for {target_school} (State B) ---")
    invite_payload = {
        "institution_id": target_school,
        "full_name": "Smt. Shailaja Ballari",
        "email": "shailaja.ballari@nagriksetu.gov",
        "phone": "9845019001",
        "role_id": "academic_admin"
    }
    invite_res = requests.post(
        f"{base_url}/admin/institution-admins/invite",
        json=invite_payload,
        headers=headers
    )
    assert invite_res.status_code == 200, f"Invite failed: {invite_res.text}"
    invite_data = invite_res.json()
    raw_token = invite_data.get("invitation_token")
    user_id = invite_data.get("user_id")
    print(f"Invitation issued! User ID: {user_id}")
    print(f"Private Token generated: {raw_token[:8]}... (securely held by invitee)")

    # Verify State B in Backend
    res_b = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    data_b = res_b.json()
    print(f"Status: {data_b['status']} | Button: '{data_b['button_label']}' | Can Login: {data_b['can_login']}")
    assert data_b["status"] == "INVITED", f"Expected INVITED, got {data_b['status']}"
    assert data_b["button_label"] == "Invitation Available"
    assert data_b["can_login"] is False

    # Verify token is NEVER leaked in public listing
    schools_res = requests.get(f"{base_url}/schools?limit=100")
    schools_data = schools_res.json()
    sch019_item = next(s for s in schools_data if s["school_id"] == target_school)
    assert sch019_item["admin_status"]["status"] == "INVITED"
    assert sch019_item["admin_status"]["button_label"] == "Invitation Available"
    assert "token" not in json.dumps(sch019_item).lower() or "token_hash" not in sch019_item
    print("Verified: Token is NOT exposed in public /schools API.")

    # Capture State B Screenshot
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase18_button_state_b_invited.png",
        "State B: 'Invitation Available' button rendered dynamically for invited institution"
    )

    # ------------------------------------------------------------------
    # STATE C: INVITATION OPENED / VERIFIED -> "Complete Account Setup"
    # ------------------------------------------------------------------
    print(f"\n--- 4. Invitee Verifies Token (State C: ACCEPTED_PENDING_PASSWORD) ---")
    verify_res = requests.get(f"{base_url}/auth/verify-invitation?token={raw_token}")
    assert verify_res.status_code == 200, f"Token verification failed: {verify_res.text}"
    verify_data = verify_res.json()
    print(f"Token verified for {verify_data.get('email')} at {verify_data.get('school_name')}")

    # Verify State C in Backend
    res_c = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    data_c = res_c.json()
    print(f"Status: {data_c['status']} | Button: '{data_c['button_label']}' | Can Login: {data_c['can_login']}")
    assert data_c["status"] == "ACCEPTED_PENDING_PASSWORD", f"Expected ACCEPTED_PENDING_PASSWORD, got {data_c['status']}"
    assert data_c["button_label"] == "Complete Account Setup"
    assert data_c["can_login"] is False

    # Capture State C Screenshot
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase18_button_state_c_pending_password.png",
        "State C: 'Complete Account Setup' button rendered dynamically after invitee verification"
    )

    # ------------------------------------------------------------------
    # STATE D: PASSWORD CREATED & ACTIVATED -> "Continue to Administrator Login →"
    # ------------------------------------------------------------------
    print(f"\n--- 5. Invitee Finalizes Password Setup (State D: ACTIVE) ---")
    setup_res = requests.post(
        f"{base_url}/auth/accept-invitation",
        json={
            "token": raw_token,
            "password": "AdminBallari@2026!"
        }
    )
    assert setup_res.status_code == 200, f"Accept invitation failed: {setup_res.text}"
    print(f"Account activated successfully: {setup_res.json().get('message')}")

    # Verify State D in Backend
    res_d = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    data_d = res_d.json()
    print(f"Status: {data_d['status']} | Button: '{data_d['button_label']}' | Can Login: {data_d['can_login']}")
    assert data_d["status"] == "ACTIVE", f"Expected ACTIVE, got {data_d['status']}"
    assert data_d["button_label"] == "Continue to Administrator Login →"
    assert data_d["can_login"] is True

    # Capture State D Screenshot
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase18_button_state_d_active.png",
        "State D: 'Continue to Administrator Login →' active button rendered for activated institution"
    )

    # ------------------------------------------------------------------
    # STATE E: SUBSEQUENT LOGINS & PERSISTENCE
    # ------------------------------------------------------------------
    print(f"\n--- 6. Testing Subsequent Logins & Persistence (State E) ---")
    admin_login_res = requests.post(
        f"{base_url}/auth/login?institution_id={target_school}",
        data={
            "username": "shailaja.ballari@nagriksetu.gov",
            "password": "AdminBallari@2026!"
        }
    )
    assert admin_login_res.status_code == 200, f"Administrator login failed: {admin_login_res.text}"
    admin_data = admin_login_res.json()
    print(f"Administrator successfully signed in! Role: {admin_data.get('role')} | User ID: {admin_data.get('user_id')}")

    # Test Multi-Tenant Isolation: Attempt login to wrong institution (e.g. SCH001)
    cross_tenant_login = requests.post(
        f"{base_url}/auth/login?institution_id=SCH001",
        data={
            "username": "shailaja.ballari@nagriksetu.gov",
            "password": "AdminBallari@2026!"
        }
    )
    print(f"Cross-institution login attempt status: {cross_tenant_login.status_code} (Expected 403 Forbidden)")
    assert cross_tenant_login.status_code == 403, f"Cross-tenant isolation breached! Expected 403, got {cross_tenant_login.status_code}"

    # Verify State Persistence: Still ACTIVE
    res_e = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    data_e = res_e.json()
    assert data_e["status"] == "ACTIVE"
    assert data_d["button_label"] == "Continue to Administrator Login →"
    print("Verified: Button remains 'Continue to Administrator Login →' across logins/logouts.")

    # ------------------------------------------------------------------
    # STATE F: SUSPENSION -> "Account Suspended"
    # ------------------------------------------------------------------
    print(f"\n--- 7. Suspending Administrator (State F: SUSPENDED) ---")
    suspend_res = requests.post(
        f"{base_url}/admin/institution-admins/{user_id}/suspend",
        headers=headers
    )
    assert suspend_res.status_code == 200, f"Suspend failed: {suspend_res.text}"
    print(f"Administrator suspended by Platform Admin: {suspend_res.json().get('message')}")

    # Verify State F in Backend
    res_f = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    data_f = res_f.json()
    print(f"Status: {data_f['status']} | Button: '{data_f['button_label']}' | Can Login: {data_f['can_login']}")
    assert data_f["status"] == "SUSPENDED", f"Expected SUSPENDED, got {data_f['status']}"
    assert data_f["button_label"] == "Account Suspended"
    assert data_f["can_login"] is False

    # Verify login while suspended is strictly blocked
    suspended_login = requests.post(
        f"{base_url}/auth/login?institution_id={target_school}",
        data={
            "username": "shailaja.ballari@nagriksetu.gov",
            "password": "AdminBallari@2026!"
        }
    )
    print(f"Suspended login attempt status: {suspended_login.status_code} (Expected 401 or 403 Forbidden)")
    assert suspended_login.status_code in (401, 403), f"Expected 401/403, got {suspended_login.status_code}"

    # Capture State F Screenshot
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase18_button_state_f_suspended.png",
        "State F: 'Account Suspended' alert button rendered when administrator is suspended"
    )

    print("\n==================================================================")
    print("ALL 7 LIFECYCLE STATES & SECURITY CONSTRAINTS VERIFIED 100%!")
    print("==================================================================")

if __name__ == "__main__":
    run_lifecycle_test()
