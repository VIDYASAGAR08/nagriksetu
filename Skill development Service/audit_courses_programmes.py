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
    print("=== 1. ALL TRAINING CENTRES IN DB ===")
    cur.execute("SELECT id, code, name, location, district, state, active FROM training_centres ORDER BY id")
    centres = cur.fetchall()
    centre_map = {c['id']: c for c in centres}
    for c in centres:
        print(f"ID: {c['id']} | Code: {c['code']} | Name: {c['name']} | Location: {c['location']} | District: {c['district']} | Active: {c['active']}")

    print("\n=== 2. ALL SKILLS IN DB ===")
    cur.execute("SELECT id, code, name, category_name, level, duration_weeks, duration_hours, enrolled_count, active FROM skills ORDER BY id")
    skills = cur.fetchall()
    skill_map = {s['id']: s for s in skills}
    print(f"Total skills: {len(skills)}")
    for s in skills:
        print(f"ID: {s['id']} | Code: {s['code']} | Name: {s['name']} | Category: {s['category_name']} | Level: {s['level']}")

    print("\n=== 3. ALL TRAINING PROGRAMS IN DB ===")
    cur.execute("""
        SELECT tp.id, tp.code, tp.skill_id, tp.title, tp.provider_name, tp.trainer_id, tp.centre_id, tp.mode, tp.duration_hours, tp.fee, tp.status,
               s.name as skill_name, s.code as skill_code,
               tc.name as centre_name, tc.code as centre_code, tc.district as centre_district, tc.state as centre_state
        FROM training_programs tp
        LEFT JOIN skills s ON tp.skill_id = s.id
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        ORDER BY tp.id
    """)
    programs = cur.fetchall()
    print(f"Total training programs: {len(programs)}")
    
    missing_centre = []
    invalid_centre = []
    valid_centre = []

    for p in programs:
        c_id = p['centre_id']
        if c_id is None:
            missing_centre.append(p)
            status_str = "MISSING CENTRE_ID (NULL)"
        elif c_id not in centre_map:
            invalid_centre.append(p)
            status_str = f"INVALID CENTRE_ID ({c_id} NOT IN training_centres)"
        else:
            valid_centre.append(p)
            status_str = f"OK -> Centre #{c_id} ({p['centre_code']}: {p['centre_name']})"
        
        print(f"Program ID: {p['id']} | Code: {p['code']} | Title: '{p['title']}' | Skill: '{p['skill_name']}' (ID {p['skill_id']}) | CentreID: {c_id} | Status: {status_str}")

    print("\n=== AUDIT SUMMARY FOR TRAINING PROGRAMS ===")
    print(f"Total Programs: {len(programs)}")
    print(f"Valid Mappings: {len(valid_centre)}")
    print(f"Missing (NULL) Mappings: {len(missing_centre)}")
    print(f"Invalid (Non-existent) Mappings: {len(invalid_centre)}")

    # Let's check how batches relate to programs / centres
    print("\n=== 4. BATCHES AUDIT ===")
    cur.execute("""
        SELECT b.id, b.code, b.program_id, b.batch_name, b.mode, b.total_seats, b.available_seats, b.status,
               tp.title as program_title, tp.centre_id, tc.name as centre_name
        FROM batches b
        LEFT JOIN training_programs tp ON b.program_id = tp.id
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        ORDER BY b.id
    """)
    batches = cur.fetchall()
    print(f"Total batches: {len(batches)}")
    for b in batches:
        print(f"Batch ID: {b['id']} | Code: {b['code']} | Name: {b['batch_name']} | Program ID: {b['program_id']} ('{b['program_title']}') | Centre ID: {b['centre_id']} ({b['centre_name']})")

    # Let's check enrollments/applications per program/centre
    print("\n=== 5. ENROLLMENTS RELATIONSHIP CHECK ===")
    cur.execute("""
        SELECT e.id, e.citizen_ref, e.program_id, e.centre_id, e.status,
               tp.centre_id as program_centre_id,
               tc_e.name as enrollment_centre_name,
               tc_p.name as program_centre_name
        FROM enrollments e
        LEFT JOIN training_programs tp ON e.program_id = tp.id
        LEFT JOIN training_centres tc_e ON e.centre_id = tc_e.id
        LEFT JOIN training_centres tc_p ON tp.centre_id = tc_p.id
        LIMIT 20
    """)
    enrollments_sample = cur.fetchall()
    print(f"Sample of enrollments (total rows: check mismatch between e.centre_id and tp.centre_id):")
    cur.execute("""
        SELECT COUNT(*) as mismatch_count
        FROM enrollments e
        JOIN training_programs tp ON e.program_id = tp.id
        WHERE e.centre_id != tp.centre_id OR (e.centre_id IS NULL AND tp.centre_id IS NOT NULL) OR (e.centre_id IS NOT NULL AND tp.centre_id IS NULL)
    """)
    mismatch = cur.fetchone()
    print("Enrollment vs Program centre_id mismatches:", mismatch['mismatch_count'])

conn.close()
