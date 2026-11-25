import pymysql
import json

conn = pymysql.connect(
    host="localhost",
    port=3308,
    user="nagriksetu_skill",
    password="skill-app-pass-2026",
    database="skill_db",
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    # 1. Fetch all centres
    cur.execute("SELECT id, code, name, district, location, approval_status, active FROM training_centres ORDER BY id")
    centres = cur.fetchall()
    print(f"Total centres in DB: {len(centres)}")

    centre_offerings = []
    for c in centres:
        # Fetch programmes offered by this centre
        cur.execute("""
            SELECT p.id as prog_id, p.code as prog_code, p.title as prog_title, p.mode as prog_mode,
                   s.id as skill_id, s.code as skill_code, s.name as skill_name,
                   c.name as cat_name, sub.name as subcat_name
            FROM training_programs p
            JOIN skills s ON p.skill_id = s.id
            JOIN categories c ON s.category_id = c.id
            LEFT JOIN subcategories sub ON s.subcategory_id = sub.id
            WHERE p.centre_id = %s
            ORDER BY p.id
        """, (c["id"],))
        progs = cur.fetchall()

        # Fetch distinct skills, categories, subcategories
        cats = sorted(list(set(p["cat_name"] for p in progs if p["cat_name"])))
        subcats = sorted(list(set(p["subcat_name"] for p in progs if p["subcat_name"])))
        skills = sorted(list(set(p["skill_name"] for p in progs if p["skill_name"])))

        # Batches count
        cur.execute("""
            SELECT COUNT(b.id) as batch_count,
                   SUM(b.total_seats) as total_seats,
                   SUM(b.available_seats) as avail_seats
            FROM batches b
            JOIN training_programs p ON b.program_id = p.id
            WHERE p.centre_id = %s
        """, (c["id"],))
        b_info = cur.fetchone()

        centre_offerings.append({
            "id": c["id"],
            "code": c["code"],
            "name": c["name"],
            "district": c["district"],
            "location": c["location"],
            "active": c["active"],
            "program_count": len(progs),
            "batch_count": b_info["batch_count"],
            "total_seats": b_info["total_seats"],
            "available_seats": b_info["avail_seats"],
            "categories": cats,
            "subcategories": subcats,
            "skills": skills,
            "program_list": [{"code": p["prog_code"], "title": p["prog_title"], "mode": p["prog_mode"]} for p in progs]
        })

    for co in centre_offerings:
        print(f"\n=======================================================")
        print(f"[{co['code']}] {co['name']} ({co['district']})")
        print(f"  Status: {'Active' if co['active'] else 'Inactive'}")
        print(f"  Programmes Offered: {co['program_count']} | Batches: {co['batch_count']} | Seats: {co['available_seats']}/{co['total_seats']}")
        print(f"  Categories ({len(co['categories'])}): {', '.join(co['categories'])}")
        print(f"  Subcategories ({len(co['subcategories'])}): {', '.join(co['subcategories'])}")
        print(f"  Skills ({len(co['skills'])}): {', '.join(co['skills'][:6])}{'...' if len(co['skills']) > 6 else ''}")

conn.close()
