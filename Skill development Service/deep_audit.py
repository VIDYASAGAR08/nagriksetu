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
    print("=== 1. EXACT PROGRAMME COUNT PER CENTRE (FROM DB) ===")
    cur.execute("""
        SELECT tc.id as centre_id, tc.code as centre_code, tc.name as centre_name, tc.district, tc.state, tc.active,
               COUNT(tp.id) as exact_programme_count
        FROM training_centres tc
        LEFT JOIN training_programs tp ON tc.id = tp.centre_id
        WHERE tc.active = 1
        GROUP BY tc.id, tc.code, tc.name, tc.district, tc.state, tc.active
        ORDER BY tc.id
    """)
    centres_db = cur.fetchall()
    total_progs_centres = 0
    for c in centres_db:
        total_progs_centres += c['exact_programme_count']
        print(f"Centre #{c['centre_id']} ({c['centre_code']}) {c['centre_name']}: {c['exact_programme_count']} programmes")
    print(f"Total programmes mapped across active centres: {total_progs_centres}")

    print("\n=== 2. LIST EVERY PROGRAMME ID GROUPED BY CENTRE_ID ===")
    cur.execute("""
        SELECT tp.centre_id, tp.id as program_id, tp.code as program_code, tp.title, tp.skill_id
        FROM training_programs tp
        ORDER BY tp.centre_id, tp.id
    """)
    progs_all = cur.fetchall()
    progs_by_c = {}
    for p in progs_all:
        progs_by_c.setdefault(p['centre_id'], []).append(p)

    for c in centres_db:
        cid = c['centre_id']
        plist = progs_by_c.get(cid, [])
        p_ids = [p['program_id'] for p in plist]
        p_codes = [p['program_code'] for p in plist]
        print(f"\nCentre #{cid} ({c['centre_code']} - {c['centre_name']}):")
        print(f"  Count: {len(plist)}")
        print(f"  Programme IDs ({len(p_ids)}): {p_ids}")
        print(f"  Programme Codes: {p_codes}")

    print("\n=== 3. VERIFY ALL 125 PROGRAMME IDS ARE UNIQUE & VALID ===")
    cur.execute("SELECT id, code, centre_id FROM training_programs")
    all_p = cur.fetchall()
    ids = [p['id'] for p in all_p]
    codes = [p['code'] for p in all_p]
    null_centres = [p for p in all_p if p['centre_id'] is None]
    
    # Check if any centre_id is not in active training_centres
    active_centre_ids = {c['centre_id'] for c in centres_db}
    invalid_centres = [p for p in all_p if p['centre_id'] not in active_centre_ids]

    print(f"Total rows in training_programs: {len(all_p)}")
    print(f"Distinct IDs: {len(set(ids))} (Min ID: {min(ids)}, Max ID: {max(ids)})")
    print(f"Distinct Codes: {len(set(codes))}")
    print(f"Programmes with NULL centre_id: {len(null_centres)}")
    print(f"Programmes with invalid/inactive centre_id: {len(invalid_centres)}")

    print("\n=== 4. INVESTIGATE SKL-0105 TO SKL-0125 ===")
    cur.execute("""
        SELECT id, code, name, category_name, active, created_at, enrolled_count
        FROM skills
        WHERE id >= 105 AND id <= 125
        ORDER BY id
    """)
    unlinked_skills = cur.fetchall()
    for s in unlinked_skills:
        print(f"Skill ID: {s['id']} | Code: {s['code']} | Active: {s['active']} | Name: '{s['name']}'")

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
