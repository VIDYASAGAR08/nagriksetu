import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

test_cases = [
    ("SCH001", "SCH01125", "School: Government Model School"),
    ("COL003", "COL03001", "Degree College: BMS College of Engineering"),
    ("SCH011", "SCH11097", "PU College: Tumakuru Model Pre-University College"),
    ("SCH016", "SCH16097", "School: Belagavi Public School"),
    ("SCH020", "SCH20097", "School: Kalaburagi Public School")
]

print("=== TESTING STUDENT DOSSIER DATA INTEGRITY ===")
for inst_id, sid, desc in test_cases:
    print(f"\n--- Testing {desc} (ID: {sid}) ---")
    row = cur.execute("""
        SELECT s.*, sch.school_name, sch.school_type, sch.category
        FROM students s
        JOIN schools sch ON sch.school_id = s.school_id
        WHERE (s.student_id = ? OR s.permanent_student_id = ?) AND s.school_id = ?
    """, (sid, sid, inst_id)).fetchone()
    
    if not row:
        print(f"FAILED: Student {sid} not found in {inst_id}!")
        continue
    
    st = dict(row)
    psid = st["permanent_student_id"]
    
    # 1. Personal Info
    print(f"  Name: {st['student_name']} | DOB: {st['date_of_birth']} | Gender: {st['gender']} | Blood: {st['blood_group']} | Category: {st['social_category']}")
    print(f"  Address: {st['address']} | PIN: {st['pincode']}")
    
    # 2. Guardians
    g_rows = cur.execute("""
        SELECT g.full_name, g.relationship, g.phone, g.email
        FROM student_guardians sg
        JOIN guardians g ON g.guardian_id = sg.guardian_id
        WHERE sg.permanent_student_id = ?
    """, (psid,)).fetchall()
    print(f"  Verified Guardians: {len(g_rows)} -> {[dict(g) for g in g_rows]}")
    
    # 3. Academic
    e_row = cur.execute("SELECT * FROM enrollments WHERE permanent_student_id = ? AND school_id = ?", (psid, inst_id)).fetchone()
    if e_row:
        enr = dict(e_row)
        print(f"  Enrollment: Std={enr.get('standard')}, Sec={enr.get('section')}, Stream={enr.get('stream')}, Prog={enr.get('program_id')}, Degree={enr.get('degree')}")
    else:
        print("  Enrollment: None")
        
    # 4. Attendance
    att_rows = cur.execute("SELECT attendance_date, status FROM student_attendance WHERE permanent_student_id = ?", (psid,)).fetchall()
    present_cnt = sum(1 for a in att_rows if a["status"] == "present")
    pct = round((present_cnt / len(att_rows)) * 100, 1) if att_rows else 0
    print(f"  Attendance: Total={len(att_rows)} days, Present={present_cnt}, Percentage={pct}%")
    
    # 5. Results
    res_rows = cur.execute("SELECT subject_name, exam_name, marks_obtained, maximum_marks, grade, percentage FROM academic_results WHERE permanent_student_id = ?", (psid,)).fetchall()
    print(f"  Results: Total={len(res_rows)} subjects")
    for r in res_rows[:3]:
        print(f"    Subj: {r['subject_name']} -> {r['marks_obtained']}/{r['maximum_marks']} ({r['percentage']}%, Grade {r['grade']})")
        
    # 6. Documents
    doc_rows = cur.execute("SELECT document_type, file_name, verification_status FROM student_documents WHERE permanent_student_id = ?", (psid,)).fetchall()
    print(f"  Documents: Total={len(doc_rows)} files")
    for d in doc_rows:
        print(f"    Doc: {d['document_type']} ({d['file_name']}) -> {d['verification_status']}")

conn.close()
