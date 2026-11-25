import pymysql
import json
from decimal import Decimal

def default_json(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

conn = pymysql.connect(
    host="localhost",
    port=3308,
    user="nagriksetu_skill",
    password="skill-app-pass-2026",
    database="skill_db",
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT id, code, name, district, location, approval_status, active
        FROM training_centres
        WHERE active = 1
        ORDER BY id
    """)
    centres = cur.fetchall()

    result = []
    for c in centres:
        cur.execute("""
            SELECT p.id as prog_id, p.code as prog_code, p.title as prog_title, p.mode as prog_mode,
                   s.id as skill_id, s.name as skill_name,
                   cat.name as cat_name, sub.name as subcat_name
            FROM training_programs p
            JOIN skills s ON p.skill_id = s.id
            JOIN categories cat ON s.category_id = cat.id
            LEFT JOIN subcategories sub ON s.subcategory_id = sub.id
            WHERE p.centre_id = %s
            ORDER BY p.id
        """, (c["id"],))
        progs = cur.fetchall()

        cur.execute("""
            SELECT COUNT(b.id) as batch_count,
                   COALESCE(SUM(b.total_seats), 0) as total_seats,
                   COALESCE(SUM(b.available_seats), 0) as avail_seats
            FROM batches b
            JOIN training_programs p ON b.program_id = p.id
            WHERE p.centre_id = %s
        """, (c["id"],))
        b_info = cur.fetchone()

        cats = sorted(list(set(p["cat_name"] for p in progs if p["cat_name"])))
        subcats = sorted(list(set(p["subcat_name"] for p in progs if p["subcat_name"])))
        skills = sorted(list(set(p["skill_name"] for p in progs if p["skill_name"])))

        entry = {
            "centre_id": c["id"],
            "centre_code": c["code"],
            "centre_name": c["name"],
            "district": c["district"],
            "location": c["location"],
            "programme_count": len(progs),
            "batch_count": b_info["batch_count"],
            "total_seats": int(b_info["total_seats"]),
            "available_seats": int(b_info["avail_seats"]),
            "categories": cats,
            "subcategories": subcats,
            "skills_count": len(skills),
            "skills": skills,
            "programmes": [{"code": p["prog_code"], "title": p["prog_title"], "mode": p["prog_mode"], "skill": p["skill_name"]} for p in progs]
        }
        result.append(entry)

    with open("C:/Users/karth/OneDrive/Documents/NagrikSetu_Skill_Development_FINAL/centres_10_breakdown.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=default_json)

    for r in result:
        print(f"\n=======================================================")
        print(f"[{r['centre_code']}] {r['centre_name']} (DB ID: {r['centre_id']}, District: {r['district']})")
        print(f"  Programmes: {r['programme_count']} | Batches: {r['batch_count']} | Seats: {r['available_seats']} / {r['total_seats']}")
        print(f"  Categories ({len(r['categories'])}): {', '.join(r['categories'])}")
        print(f"  Subcategories ({len(r['subcategories'])}): {', '.join(r['subcategories'])}")

conn.close()
