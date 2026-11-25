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
    # 1. Fetch all training centres
    cur.execute("SELECT id, code, name, location, district, state, active FROM training_centres ORDER BY id")
    centres = cur.fetchall()
    centre_map = {c['id']: c for c in centres}

    # 2. Fetch all skills (Explore Skills & All Courses)
    cur.execute("SELECT id, code, name, category_name, level, duration_weeks, duration_hours, active FROM skills ORDER BY id")
    skills = cur.fetchall()
    skill_map = {s['id']: s for s in skills}

    # 3. Fetch all training programs
    cur.execute("""
        SELECT tp.id, tp.code, tp.skill_id, tp.title, tp.provider_name, tp.trainer_id, tp.centre_id, tp.mode, tp.duration_hours, tp.fee, tp.status,
               s.name as skill_name, s.code as skill_code, s.category_name,
               tc.name as centre_name, tc.code as centre_code, tc.district as centre_district, tc.state as centre_state, tc.active as centre_active
        FROM training_programs tp
        LEFT JOIN skills s ON tp.skill_id = s.id
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        ORDER BY tp.id
    """)
    programs = cur.fetchall()

    # 4. Fetch all batches
    cur.execute("SELECT id, code, program_id, batch_name, status, total_seats, available_seats FROM batches ORDER BY id")
    batches = cur.fetchall()
    prog_batches = {}
    for b in batches:
        prog_batches.setdefault(b['program_id'], []).append(b)

    # 5. Check mapping per skill
    skill_to_programs = {}
    for p in programs:
        skill_to_programs.setdefault(p['skill_id'], []).append(p)

    # Compile comprehensive audit data
    audit_results = {
        "total_centres": len(centres),
        "active_accredited_centres": len([c for c in centres if c['active'] == 1]),
        "total_skills": len(skills),
        "total_programs": len(programs),
        "total_batches": len(batches),
        "programs_by_centre": {},
        "missing_centre_programs": [],
        "invalid_centre_programs": [],
        "inactive_centre_programs": [],
        "skills_without_programs": [],
        "skills_audit": [],
        "programs_audit": []
    }

    for p in programs:
        c_id = p['centre_id']
        p_info = {
            "program_id": p['id'],
            "program_code": p['code'],
            "program_title": p['title'],
            "skill_id": p['skill_id'],
            "skill_code": p['skill_code'],
            "skill_name": p['skill_name'],
            "category": p['category_name'],
            "centre_id": c_id,
            "centre_code": p['centre_code'],
            "centre_name": p['centre_name'],
            "centre_district": p['centre_district'],
            "centre_state": p['centre_state'],
            "centre_active": p['centre_active'],
            "mode": p['mode'],
            "fee": p['fee'],
            "status": p['status'],
            "batch_count": len(prog_batches.get(p['id'], []))
        }

        if c_id is None:
            audit_results["missing_centre_programs"].append(p_info)
        elif c_id not in centre_map:
            audit_results["invalid_centre_programs"].append(p_info)
        else:
            if not p['centre_active']:
                audit_results["inactive_centre_programs"].append(p_info)
            audit_results["programs_by_centre"].setdefault(c_id, []).append(p_info)

        audit_results["programs_audit"].append(p_info)

    for s in skills:
        s_progs = skill_to_programs.get(s['id'], [])
        associated_centres = list({prg['centre_name'] for prg in s_progs if prg['centre_name']})
        associated_centre_ids = list({prg['centre_id'] for prg in s_progs if prg['centre_id']})
        s_info = {
            "skill_id": s['id'],
            "skill_code": s['code'],
            "skill_name": s['name'],
            "category": s['category_name'],
            "level": s['level'],
            "programs_count": len(s_progs),
            "associated_centre_ids": associated_centre_ids,
            "associated_centres": associated_centres
        }
        if len(s_progs) == 0:
            audit_results["skills_without_programs"].append(s_info)
        audit_results["skills_audit"].append(s_info)

    with open("audit_full_dump.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print("Audit dump generated successfully.")
    print("Summary:")
    print(f"Total Centres in DB: {audit_results['total_centres']} (Active: {audit_results['active_accredited_centres']})")
    print(f"Total Skills / Courses: {audit_results['total_skills']}")
    print(f"Total Training Programmes: {audit_results['total_programs']}")
    print(f"Missing Centre Mappings: {len(audit_results['missing_centre_programs'])}")
    print(f"Invalid Centre Mappings: {len(audit_results['invalid_centre_programs'])}")
    print(f"Inactive Centre Mappings: {len(audit_results['inactive_centre_programs'])}")
    print(f"Skills without any Programmes: {len(audit_results['skills_without_programs'])}")

    print("\nProgrammes count per active centre:")
    for cid, plist in sorted(audit_results['programs_by_centre'].items()):
        c = centre_map[cid]
        print(f" Centre #{cid} ({c['code']} - {c['name']}): {len(plist)} programmes")

conn.close()
