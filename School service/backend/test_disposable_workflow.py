"""
test_disposable_workflow.py
Validates end-to-end workflow on nagriksetu_disposable.db
"""
import sqlite3
import hashlib
import uuid
import time

DISPOSABLE_DB = 'C:/Users/callm/nagriksetu/backend/data/nagriksetu_disposable.db'

def mask_phone(phone: str) -> str:
    if not phone or len(phone) < 10:
        return "XXXXXX" + (phone[-4:] if phone else "")
    return f"+91 {phone[:2]}••••••{phone[-2:]}"

def test_workflow():
    conn = sqlite3.connect(DISPOSABLE_DB)
    c = conn.cursor()

    # Step 1: Public directory query for SCH001 students
    students = c.execute('''
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.standard, s.section, s.enrollment_status
        FROM students s
        WHERE s.school_id = 'SCH001' AND s.standard = 1 AND s.section = 'A'
        LIMIT 5
    ''').fetchall()
    assert len(students) > 0, "No students found"
    target_student = students[0]
    psid = target_student[1]
    print(f"1. Target Student for Edit: {target_student[2]} ({psid})")

    # Step 2: Retrieve masked parent admission contacts
    contact = c.execute('''
        SELECT father_name, father_phone, mother_name, mother_phone
        FROM student_admission_contacts
        WHERE permanent_student_id = ?
    ''', (psid,)).fetchone()
    assert contact is not None, "Admission contact missing"
    
    masked_father = mask_phone(contact[1])
    masked_mother = mask_phone(contact[3])
    print(f"2. Masked Parent Options:")
    print(f"   Option A: Father - {masked_father}")
    print(f"   Option B: Mother - {masked_mother}")

    # Step 3: Send OTP for Father
    selected_role = "father"
    target_phone = contact[1]
    raw_otp = "852963"
    otp_hash = hashlib.sha256(raw_otp.encode()).hexdigest()
    session_id = str(uuid.uuid4())
    expires_at = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 600))

    c.execute('''
        INSERT INTO parent_otp_verifications (session_id, permanent_student_id, contact_role, phone, otp_hash, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, psid, selected_role, target_phone, otp_hash, expires_at))
    conn.commit()
    print(f"3. OTP Sent to Father. Session ID: {session_id[:8]}...")

    # Step 4: Verify OTP and create/link parent guardian account
    # Check OTP
    otp_record = c.execute('''
        SELECT session_id, permanent_student_id, contact_role, phone, otp_hash, attempts, max_attempts, expires_at, is_verified
        FROM parent_otp_verifications
        WHERE session_id = ?
    ''', (session_id,)).fetchone()
    assert otp_record is not None
    assert otp_record[4] == hashlib.sha256(raw_otp.encode()).hexdigest(), "OTP hash mismatch"
    
    # Mark verified
    c.execute('UPDATE parent_otp_verifications SET is_verified = 1 WHERE session_id = ?', (session_id,))

    # Link / create parent user
    parent_user = c.execute('SELECT user_id FROM users WHERE phone = ?', (target_phone,)).fetchone()
    if not parent_user:
        parent_user_id = str(uuid.uuid4())
        c.execute('''
            INSERT INTO users (user_id, phone, password_hash, role, is_active, full_name)
            VALUES (?, ?, ?, 'parent', 1, ?)
        ''', (parent_user_id, target_phone, 'OTP_VERIFIED', contact[0]))
    else:
        parent_user_id = parent_user[0]

    # Link guardian
    guardian = c.execute('SELECT guardian_id FROM guardians WHERE user_id = ?', (parent_user_id,)).fetchone()
    if not guardian:
        guardian_id = str(uuid.uuid4())
        c.execute('''
            INSERT INTO guardians (guardian_id, user_id, full_name, relationship, phone)
            VALUES (?, ?, ?, 'Father', ?)
        ''', (guardian_id, parent_user_id, contact[0], target_phone))
    else:
        guardian_id = guardian[0]

    # Link student_guardian
    sg = c.execute('SELECT student_guardian_id FROM student_guardians WHERE permanent_student_id = ? AND guardian_id = ?', (psid, guardian_id)).fetchone()
    if not sg:
        c.execute('''
            INSERT INTO student_guardians (student_guardian_id, permanent_student_id, guardian_id, can_view_records, can_request_updates, is_verified)
            VALUES (?, ?, ?, 1, 1, 1)
        ''', (str(uuid.uuid4()), psid, guardian_id))
    conn.commit()
    print(f"4. Parent Account Authenticated & Linked: User {parent_user_id[:8]}, Guardian {guardian_id[:8]}")

    # Step 5: Parent submits update request (e.g. residential address change)
    req_id = str(uuid.uuid4())
    old_addr = c.execute('SELECT residential_address FROM student_admission_contacts WHERE permanent_student_id = ?', (psid,)).fetchone()[0]
    new_addr = "#99, 12th Cross, Indiranagar, Bengaluru, Karnataka 560038"
    
    c.execute('''
        INSERT INTO update_requests (
            request_id, permanent_student_id, guardian_id, school_id, parent_user_id,
            request_type, field_name, old_value, proposed_value, reason, status
        ) VALUES (?, ?, ?, 'SCH001', ?, 'address_change', 'residential_address', ?, ?, 'Family relocated', 'submitted')
    ''', (req_id, psid, guardian_id, parent_user_id, old_addr, new_addr))
    conn.commit()
    print(f"5. Update Request Created: {req_id[:8]} (Status: submitted)")

    # Step 6: School admin reviews requests for SCH001
    school_reqs = c.execute('''
        SELECT ur.request_id, s.student_name, ur.field_name, ur.old_value, ur.proposed_value, ur.status
        FROM update_requests ur
        JOIN students s ON s.permanent_student_id = ur.permanent_student_id
        WHERE ur.school_id = 'SCH001' AND ur.status IN ('submitted', 'pending')
    ''').fetchall()
    assert any(r[0] == req_id for r in school_reqs), "Submitted request not visible to school"
    print(f"6. School Admin View: Retrieved {len(school_reqs)} pending request(s) for SCH001")

    # Step 7: School admin approves request
    # Update official student_admission_contacts
    c.execute('''
        UPDATE student_admission_contacts
        SET residential_address = ?, updated_at = CURRENT_TIMESTAMP
        WHERE permanent_student_id = ?
    ''', (new_addr, psid))
    
    # Update request status to approved
    c.execute('''
        UPDATE update_requests
        SET status = 'approved', review_comment = 'Address proof verified from electricity bill', reviewed_at = CURRENT_TIMESTAMP
        WHERE request_id = ?
    ''', (req_id,))

    # Log to audit_logs
    c.execute('''
        INSERT INTO audit_logs (audit_id, actor_role, action, entity_type, entity_id, school_id, metadata_json)
        VALUES (?, 'school_admin', 'APPROVE_UPDATE_REQUEST', 'update_request', ?, 'SCH001', ?)
    ''', (str(uuid.uuid4()), req_id, '{"field": "residential_address"}'))
    conn.commit()
    print(f"7. School Admin Approved Request {req_id[:8]}. Official address updated.")

    # Step 8: Parent checks My Requests
    parent_view = c.execute('''
        SELECT ur.request_id, s.student_name, sc.school_name, ur.field_name, ur.old_value, ur.proposed_value, ur.status, ur.review_comment
        FROM update_requests ur
        JOIN students s ON s.permanent_student_id = ur.permanent_student_id
        JOIN schools sc ON sc.school_id = ur.school_id
        WHERE ur.parent_user_id = ?
    ''', (parent_user_id,)).fetchall()
    assert len(parent_view) > 0
    pv = parent_view[0]
    print(f"8. Parent Portal 'My Requests': Status = {pv[6]} ({pv[7]})")

    # Final verification of official record
    updated_addr = c.execute('SELECT residential_address FROM student_admission_contacts WHERE permanent_student_id = ?', (psid,)).fetchone()[0]
    assert updated_addr == new_addr, "Official record address was not updated"
    print(f"9. Official Record Verified: {updated_addr}")

    conn.close()
    print("\n[ALL WORKFLOW CHECKS PASSED ON DISPOSABLE DATABASE!]")

if __name__ == '__main__':
    test_workflow()
