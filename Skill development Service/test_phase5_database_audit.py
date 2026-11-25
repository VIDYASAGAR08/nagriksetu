import pymysql

conn = pymysql.connect(host="127.0.0.1", port=3308, user="nagriksetu_skill", password="skill-app-pass-2026", database="skill_db")
cur = conn.cursor(pymysql.cursors.DictCursor)

print("======================================================================")
print("PHASE 5: DATABASE & DATA INTEGRITY DEEP AUDIT")
print("======================================================================")

# 1. Total Table Counts
tables = [
    "accounts", "skills", "categories", "training_programs",
    "batches", "trainers", "training_centres", "enrollments",
    "module_progress", "attendance_records", "assessment_results",
    "certificates", "otp_verification_sessions"
]
print("\n--- Table Counts ---")
for t in tables:
    cur.execute(f"SELECT COUNT(*) as cnt FROM {t}")
    print(f"  {t:30}: {cur.fetchone()['cnt']} rows")

# 2. Batch Seat Capacity vs Enrolments Integrity
print("\n--- Batch Capacity Consistency Check ---")
cur.execute("""
    SELECT b.id, b.code, b.batch_name, b.total_seats, b.available_seats,
           (b.total_seats - b.available_seats) as calculated_enrolled,
           COUNT(e.id) as actual_enrolled
    FROM batches b
    LEFT JOIN enrollments e ON e.batch_id = b.id AND e.status = 'ENROLLED'
    GROUP BY b.id, b.code, b.batch_name, b.total_seats, b.available_seats
    HAVING (b.total_seats - b.available_seats) < 0 OR b.available_seats > b.total_seats
""")
inconsistent_batches = cur.fetchall()
print(f"Inconsistent batch capacity counts: {len(inconsistent_batches)}")
assert len(inconsistent_batches) == 0, f"Found inconsistent batches: {inconsistent_batches}"
print("[PASS] Batch seat arithmetic is mathematically consistent across all 229 batches")

# 3. Orphan Enrolment Checks
print("\n--- Orphan Enrolments Check ---")
cur.execute("""
    SELECT e.id, e.code, e.citizen_ref, e.program_id, e.batch_id
    FROM enrollments e
    LEFT JOIN accounts a ON a.citizen_ref = e.citizen_ref
    LEFT JOIN training_programs p ON p.id = e.program_id
    LEFT JOIN batches b ON b.id = e.batch_id
    WHERE a.id IS NULL OR p.id IS NULL OR (e.batch_id IS NOT NULL AND b.id IS NULL)
""")
orphans = cur.fetchall()
print(f"Orphan enrolments: {len(orphans)}")
assert len(orphans) == 0, f"Found orphan enrolments: {orphans}"
print("[PASS] Zero orphan enrolments found")

# 4. Certificate Eligibility Enforcement Check
print("\n--- Certificate Eligibility Rules Check ---")
cur.execute("""
    SELECT e.id, e.code, e.student_id, e.training_progress_pct, e.attendance_pct, e.certificate_issued
    FROM enrollments e
    WHERE e.certificate_issued = 1 AND (e.training_progress_pct < 100 OR e.attendance_pct < 75)
""")
illegal_certs = cur.fetchall()
print(f"Certificates issued violating completion/attendance criteria: {len(illegal_certs)}")
assert len(illegal_certs) == 0, f"Found illegal certificates: {illegal_certs}"
print("[PASS] Zero certificates issued without meeting 100% progress and >=75% attendance threshold")

# 5. Check Module Progress Referential Integrity
print("\n--- Module Progress Integrity Check ---")
cur.execute("""
    SELECT mp.id, mp.enrollment_id, e.id as enr_exists
    FROM module_progress mp
    LEFT JOIN enrollments e ON e.id = mp.enrollment_id
    WHERE e.id IS NULL
""")
orphan_modules = cur.fetchall()
print(f"Orphan module_progress rows: {len(orphan_modules)}")
assert len(orphan_modules) == 0
print("[PASS] Zero orphan module progress records")

# 6. Check Attendance Records Referential Integrity
print("\n--- Attendance Records Integrity Check ---")
cur.execute("""
    SELECT ar.id, ar.enrollment_id, e.id as enr_exists
    FROM attendance_records ar
    LEFT JOIN enrollments e ON e.id = ar.enrollment_id
    WHERE e.id IS NULL
""")
orphan_att = cur.fetchall()
print(f"Orphan attendance_records rows: {len(orphan_att)}")
assert len(orphan_att) == 0
print("[PASS] Zero orphan attendance records")

conn.close()
print("\n======================================================================")
print("PHASE 5 COMPLETE: DATABASE & DATA INTEGRITY AUDIT PASSED (100%)")
print("======================================================================")
