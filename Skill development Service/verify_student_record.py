import pymysql

conn = pymysql.connect(
    host="localhost",
    port=3308,
    user="nagriksetu_skill",
    password="skill-app-pass-2026",
    database="skill_db",
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    # 1. Inspect ENR-000104 in enrollments
    cur.execute("""
        SELECT e.id, e.code, e.citizen_id, e.citizen_ref, e.student_id, e.citizen_name,
               e.program_id, e.program_title, e.centre_id, e.centre_name, e.batch_id,
               e.status, e.selected_mode, e.attendance_pct, e.training_progress_pct, e.enrolled_date
        FROM enrollments e
        WHERE e.code = 'ENR-000104' OR e.student_id = 'STU-2026-000104'
    """)
    enr_records = cur.fetchall()
    print("Enrollments matching ENR-000104 or STU-2026-000104:")
    for r in enr_records:
        print(f"  ID: {r['id']}, Code: {r['code']}, Student ID: {r['student_id']}, Citizen: {r['citizen_name']} ({r['citizen_ref']})")
        print(f"  Program: {r['program_title']} (ID {r['program_id']}) | Centre: {r['centre_name']} (ID {r['centre_id']})")
        print(f"  Batch ID: {r['batch_id']}, Status: {r['status']}, Attendance: {r['attendance_pct']}%, Progress: {r['training_progress_pct']}%")

    # 2. Inspect corresponding account
    if enr_records:
        cit_ref = enr_records[0]["citizen_ref"]
        cur.execute("SELECT id, email, full_name, role, citizen_ref, student_id FROM accounts WHERE citizen_ref = %s", (cit_ref,))
        acc = cur.fetchone()
        print(f"\nAccount Record: {acc}")

    # 3. Inspect module progress for ENR-000104
    if enr_records:
        cur.execute("""
            SELECT mp.id, mp.enrollment_id, mp.module_title, mp.is_completed, mp.completion_date, mp.remarks
            FROM module_progress mp
            WHERE mp.enrollment_id = %s
            ORDER BY mp.id
        """, (enr_records[0]["id"],))
        mods = cur.fetchall()
        print(f"\nModule Progress Records ({len(mods)}):")
        for m in mods:
            print(f"  Module: {m['module_title']} | Completed: {m['is_completed']} | Remarks: {m['remarks']}")

    # 4. Inspect batch & trainer
    if enr_records and enr_records[0]["batch_id"]:
        cur.execute("""
            SELECT b.id, b.code, b.batch_name, b.timings, b.training_schedule, b.mode, b.start_date, b.end_date,
                   b.trainer_id, t.name as trainer_name
            FROM batches b
            LEFT JOIN trainers t ON b.trainer_id = t.id
            WHERE b.id = %s
        """, (enr_records[0]["batch_id"],))
        batch = cur.fetchone()
        print(f"\nBatch Information: {batch}")

conn.close()
