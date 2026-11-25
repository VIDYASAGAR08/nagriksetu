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
    print("--- Check the 1 enrollment mismatch ---")
    cur.execute("""
        SELECT e.id, e.citizen_ref, e.program_id, e.centre_id, e.status,
               tp.centre_id as program_centre_id,
               tc_e.name as enrollment_centre_name,
               tc_p.name as program_centre_name
        FROM enrollments e
        JOIN training_programs tp ON e.program_id = tp.id
        LEFT JOIN training_centres tc_e ON e.centre_id = tc_e.id
        LEFT JOIN training_centres tc_p ON tp.centre_id = tc_p.id
        WHERE e.centre_id != tp.centre_id OR (e.centre_id IS NULL AND tp.centre_id IS NOT NULL) OR (e.centre_id IS NOT NULL AND tp.centre_id IS NULL)
    """)
    mismatches = cur.fetchall()
    print("Mismatched enrollments:", mismatches)

    print("\n--- Check training_programs centre_id breakdown ---")
    cur.execute("""
        SELECT tp.centre_id, tc.name as centre_name, tc.code as centre_code, tc.active as centre_active, COUNT(*) as program_count
        FROM training_programs tp
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        GROUP BY tp.centre_id, tc.name, tc.code, tc.active
        ORDER BY tp.centre_id
    """)
    breakdown = cur.fetchall()
    for b in breakdown:
        print(f"Centre ID: {b['centre_id']} | Code: {b['centre_code']} | Name: {b['centre_name']} | Active: {b['centre_active']} | Program Count: {b['program_count']}")

    print("\n--- Check total count of training programs ---")
    cur.execute("SELECT COUNT(*) as total FROM training_programs")
    print("Total training programs:", cur.fetchone()['total'])

    print("\n--- Check total count of skills ---")
    cur.execute("SELECT COUNT(*) as total FROM skills")
    print("Total skills:", cur.fetchone()['total'])

    print("\n--- Check if any training_program has NULL centre_id or invalid centre_id ---")
    cur.execute("""
        SELECT tp.id, tp.code, tp.title, tp.centre_id
        FROM training_programs tp
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        WHERE tp.centre_id IS NULL OR tc.id IS NULL
    """)
    invalid_progs = cur.fetchall()
    print(f"Invalid / NULL centre_id programs count: {len(invalid_progs)}")
    for ip in invalid_progs:
        print("Invalid prog:", ip)

conn.close()
