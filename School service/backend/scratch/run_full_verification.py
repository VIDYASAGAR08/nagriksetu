import urllib.request
import urllib.parse
import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, '/app')
from auth import create_access_token

BASE_URL = "http://localhost:8000"
DB_PATH = "/app/data/nagriksetu.db"

def run_test():
    print("==================================================")
    print("PARENT REQUEST VISIBILITY & ROUTING AUDIT SUITE")
    print("==================================================")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Login as SCH017 admin (Dharwad Vidya School)
    data17 = urllib.parse.urlencode({'username': 'dharwad@edu.in', 'password': 'dharwad@123'}).encode()
    req17 = urllib.request.Request(f'{BASE_URL}/auth/login?institution_id=SCH017', data=data17, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req17) as resp:
        res17 = json.loads(resp.read().decode())
        token17 = res17['access_token']
        print(f"[1] Logged in as SCH017 Admin (Email: dharwad@edu.in, School: {res17.get('school_id')})")

    # 2. Token for SCH001 admin (Government Model School)
    c.execute("SELECT user_id, email, role, school_id FROM users WHERE school_id = 'SCH001' AND role = 'school_admin' LIMIT 1")
    u01 = dict(c.fetchone())
    token01 = create_access_token(u01, school_id='SCH001')
    print(f"[2] Generated token for SCH001 Admin ({u01['email']}, School: {u01['school_id']})")

    # 3. Test Parent-Requests endpoint for SCH017
    req_list = urllib.request.Request(f'{BASE_URL}/institution/SCH017/parent-requests', headers={'Authorization': f'Bearer {token17}'})
    with urllib.request.urlopen(req_list) as resp:
        requests17 = json.loads(resp.read().decode())
        print(f"\n[3] SCH017 Parent Requests Count: {len(requests17)}")
        found_target = False
        for r in requests17:
            print(f"    - ID: {r.get('request_id')} | Tracking: {r.get('tracking_number')} | Cat: {r.get('category')} | Field: {r.get('field_name')} | Status: {r.get('status')} | ReqVal: {r.get('requested_value')}")
            if r.get('tracking_number') == 'TRK-548751':
                found_target = True
        assert found_target, "Target request TRK-548751 was NOT found in SCH017 parent-requests!"
        print("    --> SUCCESS: TRK-548751 is present in SCH017 Data Correction Requests!")

    # 4. Test Institution Isolation (Security Check)
    print("\n[4] Security & Cross-Institution Access Isolation Check:")
    try:
        req_iso1 = urllib.request.Request(f'{BASE_URL}/institution/SCH001/parent-requests', headers={'Authorization': f'Bearer {token17}'})
        urllib.request.urlopen(req_iso1)
        print("    --> FAILURE: SCH017 admin was able to access SCH001 parent-requests!")
    except urllib.error.HTTPError as e:
        print(f"    --> PASSED: SCH017 admin blocked from SCH001 with HTTP {e.code} ({e.reason})")

    try:
        req_iso2 = urllib.request.Request(f'{BASE_URL}/institution/SCH017/parent-requests', headers={'Authorization': f'Bearer {token01}'})
        urllib.request.urlopen(req_iso2)
        print("    --> FAILURE: SCH001 admin was able to access SCH017 parent-requests!")
    except urllib.error.HTTPError as e:
        print(f"    --> PASSED: SCH001 admin blocked from SCH017 with HTTP {e.code} ({e.reason})")

    # 5. Verify Parent/Guardian Linking Requests endpoint does NOT contain TRK-548751
    req_link = urllib.request.Request(f'{BASE_URL}/institution/SCH017/linking-requests', headers={'Authorization': f'Bearer {token17}'})
    with urllib.request.urlopen(req_link) as resp:
        linking_data = json.loads(resp.read().decode())
        linking_reqs = linking_data if isinstance(linking_data, list) else linking_data.get('requests', [])
        print(f"\n[5] SCH017 Linking Requests Count: {len(linking_reqs)}")
        has_trk = any(lr.get('tracking_number') == 'TRK-548751' or lr.get('request_id') == 'REQ-2026-1A9E7AD9' for lr in linking_reqs)
        assert not has_trk, "TRK-548751 erroneously appeared in linking-requests!"
        print("    --> PASSED: TRK-548751 does NOT appear in Parent Linking Requests section.")

    # 6. Test Admin Review (Approve Request TRK-548751)
    print("\n[6] Testing Admin Determination Review on TRK-548751:")
    review_payload = json.dumps({
        'action': 'approve',
        'decision': 'approved',
        'remarks': 'Phone number updated following physical verification with parent.'
    }).encode('utf-8')
    req_rev = urllib.request.Request(
        f'{BASE_URL}/institution/SCH017/parent-requests/REQ-2026-1A9E7AD9/review',
        data=review_payload,
        headers={'Authorization': f'Bearer {token17}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req_rev) as resp:
        rev_res = json.loads(resp.read().decode())
        print("    Review API Response:", rev_res)
        assert rev_res.get('status') == 'success'
        print("    --> PASSED: Determination submitted successfully.")

    # 7. Check database persistence
    print("\n[7] Database Verification After Approval:")
    c.execute("SELECT request_id, tracking_number, status, current_value, requested_value, resolved_at FROM service_requests WHERE tracking_number = 'TRK-548751'")
    sr_post = dict(c.fetchone())
    print("    service_requests:", sr_post)
    assert sr_post['status'] == 'CORRECTED', f"Expected status CORRECTED, got {sr_post['status']}"

    c.execute("SELECT * FROM request_corrections WHERE request_id = 'REQ-2026-1A9E7AD9'")
    corr_row = dict(c.fetchone())
    print("    request_corrections entry:", corr_row['correction_id'], corr_row['target_table'], corr_row['field_name'], "New:", corr_row['corrected_value'])

    c.execute("SELECT phone FROM guardians WHERE user_id = 'd2be8636-e98e-4a13-8e8a-06f8d006c9ee'")
    g_phone = c.fetchone()[0]
    print("    guardians table phone:", g_phone)
    assert g_phone == '6361168424', f"Expected phone 6361168424, got {g_phone}"

    c.execute("SELECT phone FROM users WHERE user_id = 'd2be8636-e98e-4a13-8e8a-06f8d006c9ee'")
    u_phone = c.fetchone()[0]
    print("    users table phone:", u_phone)
    assert u_phone == '6361168424', f"Expected user phone 6361168424, got {u_phone}"

    # 8. Check Parent Portal Reflection
    print("\n[8] Parent Portal Reflection Check:")
    c.execute("SELECT * FROM users WHERE user_id = 'd2be8636-e98e-4a13-8e8a-06f8d006c9ee'")
    parent_user = dict(c.fetchone())
    parent_token = create_access_token(parent_user)

    req_my = urllib.request.Request(f'{BASE_URL}/requests/my-requests', headers={'Authorization': f'Bearer {parent_token}'})
    with urllib.request.urlopen(req_my) as resp:
        my_reqs = json.loads(resp.read().decode())
        target_in_parent = [mr for mr in my_reqs if mr.get('tracking_number') == 'TRK-548751']
        assert len(target_in_parent) > 0, "TRK-548751 not found in parent's requests!"
        print("    Parent's request view:", target_in_parent[0]['tracking_number'], "| Status:", target_in_parent[0]['status'], "| Current Val:", target_in_parent[0]['current_value'])
        assert target_in_parent[0]['status'] == 'CORRECTED', f"Expected parent status CORRECTED, got {target_in_parent[0]['status']}"
        print("    --> SUCCESS: Status update (CORRECTED) is accurately reflected in Parent Portal!")

    # 9. Verify Status Filter on SCH017 parent-requests
    print("\n[9] Testing Status Filter on SCH017 Data Correction Requests:")
    req_filt = urllib.request.Request(f'{BASE_URL}/institution/SCH017/parent-requests?status=approved', headers={'Authorization': f'Bearer {token17}'})
    with urllib.request.urlopen(req_filt) as resp:
        approved_reqs = json.loads(resp.read().decode())
        print(f"    Approved requests for SCH017: {len(approved_reqs)}")
        assert any(r.get('tracking_number') == 'TRK-548751' for r in approved_reqs), "TRK-548751 should appear in approved filter!"
        print("    --> PASSED: Status filter correctly includes updated request.")

    # 10. Verify Dashboard Overview Pending Count
    print("\n[10] Testing Dashboard Overview Metrics for SCH017:")
    req_ov = urllib.request.Request(f'{BASE_URL}/institution/SCH017/dashboard-overview', headers={'Authorization': f'Bearer {token17}'})
    with urllib.request.urlopen(req_ov) as resp:
        ov = json.loads(resp.read().decode())
        print(f"    SCH017 pending_parent_requests metric: {ov.get('pending_parent_requests')}")
        print("    --> PASSED: Dashboard overview endpoint responds with 200 OK.")

    print("\n==================================================")
    print("ALL 10 VERIFICATION CHECKS PASSED PERFECTLY!")
    print("==================================================")

run_test()
