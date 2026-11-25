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
    cur.execute("SELECT id, name, enrolled_count FROM skills WHERE enrolled_count > 0 LIMIT 10")
    print("Sample skills with stored enrolled_count in DB:")
    for r in cur.fetchall():
        print(f"  Skill {r['id']} ({r['name']}): enrolled_count = {r['enrolled_count']}")

    cur.execute("SELECT status, COUNT(*) as cnt FROM enrollments GROUP BY status")
    print("\nActual enrollments in enrollments table by status:")
    for r in cur.fetchall():
        print(f"  Status: {r['status']} -> {r['cnt']} records")

    cur.execute("""
        SELECT p.skill_id, s.name as skill_name, 
               COUNT(e.id) as all_apps,
               COUNT(CASE WHEN e.status IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED') THEN 1 END) as enrolled_records,
               COUNT(DISTINCT CASE WHEN e.status IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED') THEN e.citizen_ref END) as distinct_enrolled_students
        FROM enrollments e
        JOIN training_programs p ON e.program_id = p.id
        JOIN skills s ON p.skill_id = s.id
        GROUP BY p.skill_id, s.name
        ORDER BY enrolled_records DESC
    """)
    real_counts = cur.fetchall()
    print("\nReal database enrolment counts linked to skills:")
    for r in real_counts:
        print(f"  Skill ID {r['skill_id']} ({r['skill_name']}): All Apps={r['all_apps']}, Enrolled Records={r['enrolled_records']}, Distinct Students={r['distinct_enrolled_students']}")

conn.close()
