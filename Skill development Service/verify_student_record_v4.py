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
        SELECT *
        FROM enrollments e
        WHERE e.code = 'ENR-000104' OR e.student_id = 'STU-2026-000104'
    """)
    enr_records = cur.fetchall()
    print("Enrollments matching ENR-000104 or STU-2026-000104:")
    for r in enr_records:
        for k, v in r.items():
            print(f"  {k}: {v}")

    # 2. Inspect corresponding account
    if enr_records:
        cit_ref = enr_records[0]["citizen_ref"]
        cur.execute("SELECT id, email, full_name, role, citizen_ref, student_id FROM accounts WHERE citizen_ref = %s", (cit_ref,))
        acc = cur.fetchone()
        print(f"\nAccount Record: {acc}")

    # 3. Inspect module progress for ENR-000104
    if enr_records:
        cur.execute("""
            SELECT *
            FROM module_progress mp
            WHERE mp.enrollment_id = %s
            ORDER BY mp.id
        """, (enr_records[0]["id"],))
        mods = cur.fetchall()
        print(f"\nModule Progress Records ({len(mods)}):")
        for m in mods:
            print(f"  Module: {m.get('module_title')} | Completed: {m.get('is_completed')} | Remarks: {m.get('remarks')}")

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
