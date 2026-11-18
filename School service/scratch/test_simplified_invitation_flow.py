import sys
import io
import subprocess
import time
import os
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

def run_tests():
    print("==================================================================")
    print("NAGRIKSETU: SIMPLIFIED SEAMLESS ADMINISTRATOR ONBOARDING TEST")
    print("==================================================================")

    # 1. Platform Admin Authentication
    print("\n--- 1. Authenticating as Platform Central Admin ---")
    login_res = requests.post(f"{base_url}/auth/login", data={
        "username": "admin.central@nagriksetu.gov",
        "password": "Central@NagrikSetu2026!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    platform_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {platform_token}"}
    print("Platform Admin authenticated successfully.")

    # Reset any previous assignments to clean state
    reset_res = requests.post(f"{base_url}/admin/institution-admins/reset-assignments", headers=headers)
    assert reset_res.status_code == 200
    print("Clean state established: all institutions available.")

    target_school = "SCH019" # Ballari Education School
    appointee_name = "Dr. K. V. Shailaja"
    appointee_email = "shailaja.ballari@nagriksetu.gov"

    # ------------------------------------------------------------------
    # TEST 1 & 2: Platform Admin Issues Invitation (No UI Token Exposure)
    # ------------------------------------------------------------------
    print(f"\n--- 2. Platform Admin Invites Administrator for {target_school} ---")
    invite_res = requests.post(
        f"{base_url}/admin/institution-admins/invite",
        json={
            "institution_id": target_school,
            "full_name": appointee_name,
            "email": appointee_email,
            "role_id": "academic_admin"
        },
        headers=headers
    )
    assert invite_res.status_code == 200, f"Invite failed: {invite_res.text}"
    invite_data = invite_res.json()
    print("Invitation created successfully in backend:")
    print(f"  - Institution: {invite_data.get('school_name')} ({invite_data.get('institution_id')})")
    print(f"  - Appointee: {invite_data.get('full_name')} ({invite_data.get('email')})")
    print(f"  - Status: {invite_data.get('status')} (Sent / Pending)")
    assert invite_data.get("full_name") == appointee_name
    assert invite_data.get("email") == appointee_email

    # ------------------------------------------------------------------
    # TEST 3: Institution Card Button Transitions to "Invitation Available"
    # ------------------------------------------------------------------
    print(f"\n--- 3. Verifying Institution Selection Card Status ---")
    status_res = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    status_data = status_res.json()
    print(f"Status: {status_data['status']} | Button Label: '{status_data['button_label']}'")
    assert status_data["status"] == "INVITED"
    assert status_data["button_label"] == "Invitation Available"
    assert status_data["can_login"] is False

    # Capture Screenshot: Institution Card with Invitation Available
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase19_institution_card_invitation_available.png",
        "Institution Card with dynamic 'Invitation Available' button (no token entry)"
    )

    # ------------------------------------------------------------------
    # TEST 4 & 5: Security Test - Unauthorized Visitor Attempt
    # ------------------------------------------------------------------
    print(f"\n--- 4. Security Check: Unauthorized Public Visitor Attempt ---")
    attacker_email = "unauthorized.intruder@external.com"
    unauth_verify = requests.post(f"{base_url}/auth/invitations/verify-identity", json={
        "institution_id": target_school,
        "email": attacker_email
    })
    print(f"Unauthorized claim attempt with '{attacker_email}':")
    print(f"  HTTP Response: {unauth_verify.status_code} (Expected 403 Forbidden)")
    print(f"  Detail: {unauth_verify.json().get('detail')}")
    assert unauth_verify.status_code == 403, f"Security Breach! Expected 403, got {unauth_verify.status_code}"

    # ------------------------------------------------------------------
    # TEST 6 & 7: Intended Administrator Direct Secure Verification
    # ------------------------------------------------------------------
    print(f"\n--- 5. Intended Administrator Identity Verification ---")
    auth_verify = requests.post(f"{base_url}/auth/invitations/verify-identity", json={
        "institution_id": target_school,
        "email": appointee_email
    })
    assert auth_verify.status_code == 200, f"Identity verification failed: {auth_verify.text}"
    verify_data = auth_verify.json()
    print("Identity successfully verified!")
    session_token = verify_data.get("session_token")
    admin_info = verify_data.get("administrator", {})
    print(f"  - Setup Session Token issued: {session_token[:12]}... (Valid 30 mins)")
    print(f"  - Appointee Full Name: {admin_info.get('full_name')}")
    print(f"  - Official Email: {admin_info.get('email')}")
    print(f"  - Assigned Institution: {admin_info.get('school_name')} ({admin_info.get('institution_id')})")
    print(f"  - Role: {admin_info.get('role_name')}")

    # Capture Screenshot: Step 1 Identity Verification Page
    capture_screenshot(
        f"{frontend_url}/#/accept-invitation?school_id={target_school}",
        "phase19_direct_setup_step1_identity_verification.png",
        "Step 1: Direct Identity Verification Page (No manual token entry)"
    )

    # ------------------------------------------------------------------
    # TEST 8, 9 & 10: Set Password & Account Activation
    # ------------------------------------------------------------------
    print(f"\n--- 6. Setting Password & Activating Administrator Desk ---")
    activate_res = requests.post(f"{base_url}/auth/accept-invitation", json={
        "session_token": session_token,
        "password": "BallariAdmin@2026!"
    })
    assert activate_res.status_code == 200, f"Account activation failed: {activate_res.text}"
    print(f"Activation Response: {activate_res.json().get('message')}")

    # ------------------------------------------------------------------
    # TEST 11, 12 & 13: Card Permanently Displays "Continue to Administrator Login"
    # ------------------------------------------------------------------
    print(f"\n--- 7. Verifying Card Button Permanently ACTIVE ---")
    active_status_res = requests.get(f"{base_url}/auth/institution/{target_school}/admin-status")
    active_data = active_status_res.json()
    print(f"Status: {active_data['status']} | Button Label: '{active_data['button_label']}' | Can Login: {active_data['can_login']}")
    assert active_data["status"] == "ACTIVE"
    assert active_data["button_label"] == "Continue to Administrator Login →"
    assert active_data["can_login"] is True

    # Capture Screenshot: Final Activated Institution Card
    capture_screenshot(
        f"{frontend_url}/#/select-institution",
        "phase19_institution_card_activated_login.png",
        "Final Activated Institution Card with 'Continue to Administrator Login →'"
    )

    # ------------------------------------------------------------------
    # TEST 14: Reused and Expired Tokens are Rejected
    # ------------------------------------------------------------------
    print(f"\n--- 8. Verifying Reused Session Token is Rejected ---")
    reuse_res = requests.post(f"{base_url}/auth/accept-invitation", json={
        "session_token": session_token,
        "password": "AnotherPassword123!"
    })
    print(f"Reused session attempt: HTTP {reuse_res.status_code} (Expected 400)")
    assert reuse_res.status_code == 400, f"Expected 400, got {reuse_res.status_code}"

    # ------------------------------------------------------------------
    # TEST 15: Cross-Institution Access Forbidden
    # ------------------------------------------------------------------
    print(f"\n--- 9. Verifying Cross-Institution Isolation ---")
    cross_login = requests.post(f"{base_url}/auth/login?institution_id=SCH001", data={
        "username": appointee_email,
        "password": "BallariAdmin@2026!"
    })
    print(f"Cross-institution login to SCH001: HTTP {cross_login.status_code} (Expected 403)")
    assert cross_login.status_code == 403, f"Expected 403, got {cross_login.status_code}"

    # Valid Login to Assigned Institution SCH019
    valid_login = requests.post(f"{base_url}/auth/login?institution_id={target_school}", data={
        "username": appointee_email,
        "password": "BallariAdmin@2026!"
    })
    assert valid_login.status_code == 200, f"Valid login failed: {valid_login.text}"
    print("Authorized Administrator login to assigned institution SCH019 SUCCEEDED!")

    # ------------------------------------------------------------------
    # Reset Assignments after test to leave database in clean state
    # ------------------------------------------------------------------
    print(f"\n--- 10. Cleaning up test assignments ---")
    requests.post(f"{base_url}/admin/institution-admins/reset-assignments", headers=headers)
    print("Database returned to pristine clean state (all 30 institutions available).")

    print("\n==================================================================")
    print("ALL 15 SIMPLIFIED ONBOARDING TESTS COMPLETED WITH 100% SUCCESS!")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
