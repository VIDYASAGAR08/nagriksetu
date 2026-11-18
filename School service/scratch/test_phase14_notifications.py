import sqlite3
import requests
import json
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def login(username, password, school_id=None):
    url = f"{BASE_URL}/auth/login"
    if school_id:
        url += f"?institution_id={school_id}"
    r = requests.post(url, data={"username": username, "password": password})
    if r.status_code != 200:
        raise Exception(f"Login failed for {username} (status {r.status_code}): {r.text}")
    return r.json()["access_token"]

def main():
    print("=" * 70)
    print("NAGRIKSETU PHASE 14: NOTIFICATION MANAGEMENT AUTOMATED TEST SUITE")
    print("=" * 70)

    # Copy password hash for 8123456789 if needed
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    p_hash = c.execute("SELECT password_hash FROM users WHERE phone = '9876543210'").fetchone()[0]
    c.execute("UPDATE users SET password_hash = ? WHERE phone = '8123456789'", (p_hash,))
    conn.commit()
    conn.close()

    # Step 1: Authentication Regression Check
    print("\n[CHECK 11] Authentication Regression across all 6 roles & 4 institutional tiers...")
    tokens = {}
    tokens["student"] = login("SCH01125", "Password@2026!")
    tokens["parent_verified"] = login("9876543210", "Str0ngPass!2026")
    tokens["parent_unrelated"] = login("8123456789", "Str0ngPass!2026")
    tokens["admin_sch001"] = login("admin.sch001@example.com", "Admin@NagrikSetu2026!", "SCH001")
    tokens["admin_sch011"] = login("newadmin.sch011@example.com", "Admin@NagrikSetu2026!", "SCH011")
    tokens["admin_col001"] = login("admin.col001@example.com", "Admin@NagrikSetu2026!", "COL001")
    tokens["admin_col010"] = login("admin.col010@example.com", "Admin@NagrikSetu2026!", "COL010")
    tokens["staff_sch001"] = login("staff.sch001@example.com", "Staff@NagrikSetu2026!", "SCH001")
    tokens["platform_admin"] = login("admin.central@nagriksetu.gov", "Central@NagrikSetu2026!")

    print("  ✓ All 9 user tokens acquired successfully.")

    # Step 2: Trigger Attendance Event at SCH001 for Asha Sharma (SCH01125)
    print("\n[CHECK 1 & 2 & 3] Student & Parent Attendance Notification & Unrelated Parent Isolation...")
    att_date = "2026-11-05"
    att_payload = {
        "institution_id": "SCH001",
        "attendance_date": att_date,
        "subject_name": "Mathematics",
        "records": [
            {
                "permanent_student_id": "NS-FB8336A812DE468FB8E475443CF673EB",
                "status": "absent",
                "remarks": "Medical leave pending"
            }
        ]
    }
    r = requests.post(
        f"{BASE_URL}/academic/attendance/batch",
        json=att_payload,
        headers={"Authorization": f"Bearer {tokens['staff_sch001']}"}
    )
    assert r.status_code in (200, 201), f"Attendance batch failed: {r.text}"
    print("  ✓ Attendance marked Absent for Asha Sharma (SCH01125) on", att_date)

    # 1. Student queries notifications
    r_st = requests.get(
        f"{BASE_URL}/notifications?category=attendance",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert r_st.status_code == 200, f"Student get notifications failed: {r_st.text}"
    st_notifs = r_st.json()["items"]
    assert any("Absent" in n["title"] and att_date in n["message"] for n in st_notifs), "Student did not receive attendance alert!"
    print("  ✓ Student received attendance alert for own record.")

    # 2. Verified parent queries notifications
    r_pv = requests.get(
        f"{BASE_URL}/notifications?category=attendance",
        headers={"Authorization": f"Bearer {tokens['parent_verified']}"}
    )
    assert r_pv.status_code == 200
    pv_notifs = r_pv.json()["items"]
    assert any("Asha Sharma" in n["title"] and "Absent" in n["title"] for n in pv_notifs), "Verified parent did not receive attendance alert for linked child!"
    print("  ✓ Verified parent received attendance alert for linked child Asha Sharma.")

    # 3. Unrelated parent queries notifications
    r_pu = requests.get(
        f"{BASE_URL}/notifications",
        headers={"Authorization": f"Bearer {tokens['parent_unrelated']}"}
    )
    assert r_pu.status_code == 200
    pu_notifs = r_pu.json()["items"]
    assert not any("Asha Sharma" in n["title"] or "Asha Sharma" in n["message"] for n in pu_notifs), "LEAKAGE: Unrelated parent received notification about Asha Sharma!"
    print("  ✓ Zero leakage: Unrelated parent received no alerts about Asha Sharma.")

    # Step 3: Examination Timetable & Multi-Tenant Institution Isolation
    print("\n[CHECK 4 & 5] Examination Schedule Notification & Institution Isolation across SCH001, SCH011, COL001, COL010...")
    exam_payload = {
        "institution_id": "SCH011",
        "academic_year": "2026-2027",
        "exam_name": "Phase 14 PU Assessment Test",
        "standard_or_level": "II PUC Science",
        "start_date": "2026-11-18",
        "end_date": "2026-11-25",
        "status": "scheduled",
        "description": "Pre-University Board preparatory examination"
    }
    r = requests.post(
        f"{BASE_URL}/academic/examinations",
        json=exam_payload,
        headers={"Authorization": f"Bearer {tokens['admin_sch011']}"}
    )
    assert r.status_code == 201, f"Create exam failed: {r.text}"
    created_exam = r.json()
    print("  ✓ Examination created at SCH011:", created_exam["exam_name"])

    # PU Admin SCH011 gets notification
    r_pu_admin = requests.get(
        f"{BASE_URL}/notifications?category=examination",
        headers={"Authorization": f"Bearer {tokens['admin_sch011']}"}
    )
    assert r_pu_admin.status_code == 200
    pu_adm_notifs = r_pu_admin.json()["items"]
    assert any("Phase 14 PU Assessment Test" in n["title"] or "Phase 14 PU Assessment Test" in n["message"] for n in pu_adm_notifs), "SCH011 admin did not receive exam notification!"
    print("  ✓ SCH011 Admin received examination scheduled notification.")

    # School Admin SCH001 must NOT receive SCH011 exam notification
    r_sch_admin = requests.get(
        f"{BASE_URL}/notifications?category=examination",
        headers={"Authorization": f"Bearer {tokens['admin_sch001']}"}
    )
    assert r_sch_admin.status_code == 200
    sch_adm_notifs = r_sch_admin.json()["items"]
    assert not any("Phase 14 PU Assessment Test" in n["title"] for n in sch_adm_notifs), "ISOLATION BREACH: SCH001 Admin saw SCH011 examination!"
    print("  ✓ Institution Isolation: SCH001 Admin cannot see SCH011 examination notification.")

    # Step 4: Marks Correction & Gradebook Audit Alert to Admin
    print("\n[CHECK 5 continued] Gradebook Mark Correction Audit Notification to Institution Admin...")
    # Enter initial marks
    res_payload_1 = {
        "institution_id": "SCH001",
        "exam_name": "Midterm Examination",
        "subject_name": "Science",
        "maximum_marks": 100.0,
        "academic_year": "2026-2027",
        "records": [
            {
                "permanent_student_id": "NS-FB8336A812DE468FB8E475443CF673EB",
                "marks_obtained": 78.0
            }
        ]
    }
    requests.post(
        f"{BASE_URL}/academic/results/batch",
        json=res_payload_1,
        headers={"Authorization": f"Bearer {tokens['staff_sch001']}"}
    )

    # Now update marks with scrutiny correction
    res_payload_2 = {
        "institution_id": "SCH001",
        "exam_name": "Midterm Examination",
        "subject_name": "Science",
        "maximum_marks": 100.0,
        "academic_year": "2026-2027",
        "records": [
            {
                "permanent_student_id": "NS-FB8336A812DE468FB8E475443CF673EB",
                "marks_obtained": 91.0,
                "reason_for_change": "Re-evaluation discrepancy in Section B"
            }
        ]
    }
    r = requests.post(
        f"{BASE_URL}/academic/results/batch",
        json=res_payload_2,
        headers={"Authorization": f"Bearer {tokens['staff_sch001']}"}
    )
    assert r.status_code in (200, 201)
    print("  ✓ Marks updated from 78 to 91 for Asha Sharma.")

    # SCH001 Admin should receive Gradebook Audit Alert
    r_sch_adm = requests.get(
        f"{BASE_URL}/notifications?category=academic",
        headers={"Authorization": f"Bearer {tokens['admin_sch001']}"}
    )
    assert r_sch_adm.status_code == 200
    adm_notifs = r_sch_adm.json()["items"]
    assert any("Gradebook Audit Alert" in n["title"] and "Re-evaluation discrepancy" in n["message"] for n in adm_notifs), "SCH001 Admin did not receive Gradebook Audit Alert!"
    print("  ✓ SCH001 Admin received Gradebook Audit Alert with modification reason.")

    # COL001 Admin must NOT see SCH001 gradebook audit alert
    r_col_adm = requests.get(
        f"{BASE_URL}/notifications?category=academic",
        headers={"Authorization": f"Bearer {tokens['admin_col001']}"}
    )
    assert r_col_adm.status_code == 200
    col_adm_notifs = r_col_adm.json()["items"]
    assert not any("Gradebook Audit Alert" in n["title"] for n in col_adm_notifs), "ISOLATION BREACH: COL001 saw SCH001 gradebook audit alert!"
    print("  ✓ Degree College Admin (COL001) isolated from School Admin (SCH001) gradebook audits.")

    # Step 5: Staff Management Event & Platform Admin Monitoring
    print("\n[CHECK 6] Staff Management Event & Platform Admin Security Monitoring...")
    # Get a staff user at SCH001
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    staff_u = c.execute("SELECT user_id, email FROM users WHERE school_id = 'SCH001' AND role = 'school_staff' LIMIT 1").fetchone()
    conn.close()

    staff_uid = staff_u[0]
    # Suspend staff
    r = requests.post(
        f"{BASE_URL}/school/admin/staff/{staff_uid}/suspend",
        headers={"Authorization": f"Bearer {tokens['admin_sch001']}"}
    )
    assert r.status_code == 200
    print(f"  ✓ Staff {staff_u[1]} suspended by SCH001 Admin.")

    # Platform Admin queries security notifications
    r_plt = requests.get(
        f"{BASE_URL}/notifications?category=security",
        headers={"Authorization": f"Bearer {tokens['platform_admin']}"}
    )
    assert r_plt.status_code == 200
    plt_notifs = r_plt.json()["items"]
    assert any("Staff Suspended" in n["title"] and "SCH001" in n["title"] for n in plt_notifs), "Platform Admin did not receive security alert for staff suspension!"
    print("  ✓ Platform Admin received operational audit notification.")

    # Reactivate staff
    r = requests.post(
        f"{BASE_URL}/school/admin/staff/{staff_uid}/reactivate",
        headers={"Authorization": f"Bearer {tokens['admin_sch001']}"}
    )
    assert r.status_code == 200
    print(f"  ✓ Staff {staff_u[1]} reactivated by SCH001 Admin.")

    # Step 6: Read / Unread Functionality & Unread Count
    print("\n[CHECK 7] Read / Unread Tracking & Unread Count Endpoints...")
    r_count = requests.get(
        f"{BASE_URL}/notifications/unread-count",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert r_count.status_code == 200
    unread_init = r_count.json()["unread_count"]
    print(f"  ✓ Initial student unread count: {unread_init}")

    # Mark single notification as read
    target_notif = st_notifs[0]["notification_id"]
    r_read = requests.post(
        f"{BASE_URL}/notifications/{target_notif}/read",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert r_read.status_code == 200
    assert r_read.json()["status"] == "success"
    assert "read_at" in r_read.json()
    print("  ✓ Marked single notification as read with timestamp.")

    # Mark all as read
    r_all = requests.post(
        f"{BASE_URL}/notifications/read-all",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert r_all.status_code == 200
    print("  ✓ Marked all notifications as read.")

    r_count2 = requests.get(
        f"{BASE_URL}/notifications/unread-count",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert r_count2.json()["unread_count"] == 0
    print("  ✓ Verified unread count is now 0.")

    # Step 7: Duplicate Prevention (Idempotency)
    print("\n[CHECK 8] Duplicate Prevention & Event Idempotency...")
    # Resend the exact same attendance batch
    r_dup = requests.post(
        f"{BASE_URL}/academic/attendance/batch",
        json=att_payload,
        headers={"Authorization": f"Bearer {tokens['staff_sch001']}"}
    )
    assert r_dup.status_code in (200, 201)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    idemp_key = f"att_st:NS-FB8336A812DE468FB8E475443CF673EB:{att_date}:Mathematics:absent"
    rows = c.execute("SELECT count(*) FROM portal_notifications WHERE idempotency_key = ?", (idemp_key,)).fetchone()[0]
    conn.close()

    assert rows == 1, f"Idempotency failure! Found {rows} notifications for key {idemp_key}"
    print("  ✓ Duplicate prevention verified: Exactly 1 notification row exists despite retry.")

    # Step 8: Notification Preferences & Mandatory Alert Bypass
    print("\n[CHECK 9] Notification Preferences & Mandatory Security Bypass...")
    # 1. Disable attendance alerts in student preferences
    r_pref_upd = requests.put(
        f"{BASE_URL}/notifications/preferences",
        json={"attendance_alerts": 0, "academic_updates": 1},
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert r_pref_upd.status_code == 200
    assert r_pref_upd.json()["attendance_alerts"] == 0
    print("  ✓ Student disabled attendance alerts in preferences.")

    # 2. Trigger attendance alert for 2026-11-06
    att_payload_pref = {
        "institution_id": "SCH001",
        "attendance_date": "2026-11-06",
        "subject_name": "History",
        "records": [
            {
                "permanent_student_id": "NS-FB8336A812DE468FB8E475443CF673EB",
                "status": "absent"
            }
        ]
    }
    requests.post(
        f"{BASE_URL}/academic/attendance/batch",
        json=att_payload_pref,
        headers={"Authorization": f"Bearer {tokens['staff_sch001']}"}
    )

    # Student should NOT receive it because preference is disabled
    r_st_pref = requests.get(
        f"{BASE_URL}/notifications?category=attendance",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    st_pref_notifs = r_st_pref.json()["items"]
    assert not any("2026-11-06" in n["message"] for n in st_pref_notifs), "Disabled category notification was not suppressed!"
    print("  ✓ User preference respected: Attendance alert suppressed for student.")

    # But verified guardian with enabled preferences DID receive it
    r_pv_pref = requests.get(
        f"{BASE_URL}/notifications?category=attendance",
        headers={"Authorization": f"Bearer {tokens['parent_verified']}"}
    )
    assert any("2026-11-06" in n["message"] for n in r_pv_pref.json()["items"]), "Verified guardian should receive attendance alert!"
    print("  ✓ Verified parent received attendance alert independently.")

    # Restore student preferences
    requests.put(
        f"{BASE_URL}/notifications/preferences",
        json={"attendance_alerts": 1, "academic_updates": 1},
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )

    # Step 9: External Provider Status & Delivery Logging
    print("\n[CHECK 10] External Provider Status & Delivery Logging...")
    r_ch = requests.get(
        f"{BASE_URL}/notifications/channels/status",
        headers={"Authorization": f"Bearer {tokens['platform_admin']}"}
    )
    assert r_ch.status_code == 200
    channels = r_ch.json()
    assert channels["in_app"]["status"] == "active"
    assert channels["email"]["status"] == "provider_unavailable"
    assert channels["sms"]["status"] == "provider_unavailable"
    print("  ✓ Channel statuses accurately reported (In-app: active, Email/SMS: provider_unavailable).")

    r_logs = requests.get(
        f"{BASE_URL}/notifications/delivery-logs?limit=5",
        headers={"Authorization": f"Bearer {tokens['staff_sch001']}"}
    )
    assert r_logs.status_code == 200
    logs = r_logs.json()
    assert len(logs) > 0
    sample_log = logs[0]
    assert sample_log["status"] == "provider_unavailable"
    assert "*" in sample_log["recipient_destination"], "Recipient destination not masked!"
    print(f"  ✓ Delivery logs verified: Destination masked as '{sample_log['recipient_destination']}' with status '{sample_log['status']}'.")

    # Step 10: Database Integrity Check
    print("\n[CHECK 12] Database Integrity & Foreign Key Validation...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    integrity = c.execute("PRAGMA integrity_check").fetchone()[0]
    fks = c.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()

    assert integrity == "ok", f"Integrity check failed: {integrity}"
    assert len(fks) == 0, f"Foreign key check failed: {fks}"
    print("  ✓ PRAGMA integrity_check = ok")
    print("  ✓ PRAGMA foreign_key_check = 0 violations")

    print("\n" + "=" * 70)
    print("ALL 12 NOTIFICATION MANAGEMENT SYSTEM CHECKS PASSED (100%)")
    print("=" * 70)

if __name__ == "__main__":
    main()
