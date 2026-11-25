import pymysql
import json

conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    print("=== 4. INVESTIGATE SKL-0105 TO SKL-0125 ===")
    cur.execute("""
        SELECT id, code, name, category_name, active, enrolled_count
        FROM skills
        WHERE id >= 105 AND id <= 125
        ORDER BY id
    """)
    unlinked_skills = cur.fetchall()
    active_duplicates = []
    inactive_duplicates = []
    for s in unlinked_skills:
        print(f"Skill ID: {s['id']:3d} | Code: {s['code']:8s} | Active: {s['active']} | Enrolled: {s['enrolled_count']} | Name: '{s['name']}'")
        if s['active'] == 1:
            active_duplicates.append(s)
        else:
            inactive_duplicates.append(s)

    print(f"\nActive duplicate count: {len(active_duplicates)}")
    for a in active_duplicates:
        print(f" -> Active duplicate: ID {a['id']}, Code {a['code']}, Name: '{a['name']}'")
    print(f"Inactive duplicate count: {len(inactive_duplicates)}")

    print("\n=== 5. INVESTIGATE ENROLLMENT ID 51 ===")
    cur.execute("""
        SELECT e.id, e.citizen_ref, e.program_id, e.centre_id, e.status, e.created_at,
               tp.title as prog_title, tp.code as prog_code, tp.centre_id as prog_centre_id,
               tc.name as prog_centre_name, tc.code as prog_centre_code, tc.district as prog_centre_district
        FROM enrollments e
        LEFT JOIN training_programs tp ON e.program_id = tp.id
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        WHERE e.id = 51
    """)
    e51 = cur.fetchone()
    print("Enrollment 51 details:")
    print(json.dumps(e51, default=str, indent=2))

conn.close()
