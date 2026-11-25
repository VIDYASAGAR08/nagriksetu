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
    # 1. Total programmes
    cur.execute("SELECT COUNT(*) as cnt FROM training_programs")
    total_progs = cur.fetchone()["cnt"]

    # Mapping breakdown: which skills do the 125 programmes point to?
    cur.execute("""
        SELECT p.id, p.code, p.title, p.skill_id, s.code as skill_code, s.name as skill_name, p.centre_id
        FROM training_programs p
        LEFT JOIN skills s ON p.skill_id = s.id
        ORDER BY p.id
    """)
    all_progs = cur.fetchall()

    # Skill IDs referenced
    skill_ids_in_progs = set(p["skill_id"] for p in all_progs if p["skill_id"])
    
    # Check if any skill has multiple programmes
    cur.execute("""
        SELECT skill_id, COUNT(*) as prog_count
        FROM training_programs
        GROUP BY skill_id
        HAVING prog_count > 1
        ORDER BY prog_count DESC
    """)
    multi_progs = cur.fetchall()

    print(f"Total training programs in DB: {len(all_progs)}")
    print(f"Distinct skills referenced across all {len(all_progs)} programs: {len(skill_ids_in_progs)}")
    print(f"Skills associated with > 1 program ({len(multi_progs)} skills):")
    for mp in multi_progs:
        cur.execute("SELECT name FROM skills WHERE id = %s", (mp["skill_id"],))
        sk_name = cur.fetchone()["name"]
        print(f"  Skill ID {mp['skill_id']} ({sk_name}): {mp['prog_count']} programmes")

    # Check programmes 105 to 125
    cur.execute("""
        SELECT p.id, p.code, p.title, p.skill_id, s.name as skill_name, p.centre_id, tc.name as centre_name
        FROM training_programs p
        LEFT JOIN skills s ON p.skill_id = s.id
        LEFT JOIN training_centres tc ON p.centre_id = tc.id
        WHERE p.id > 104
        ORDER BY p.id
    """)
    progs_105_125 = cur.fetchall()
    print(f"\nProgrammes 105 to 125 breakdown ({len(progs_105_125)}):")
    for p in progs_105_125:
        print(f"  ID {p['id']} [{p['code']}]: {p['title']} -> Skill {p['skill_id']} ({p['skill_name']}) at Centre {p['centre_id']} ({p['centre_name']})")

    # Verify if any of the 104 newly added active skills have programmes
    cur.execute("""
        SELECT COUNT(*) as cnt
        FROM training_programs
        WHERE skill_id > 104
    """)
    progs_on_new_skills = cur.fetchone()["cnt"]
    print(f"\nProgrammes mapped to skills with ID > 104: {progs_on_new_skills}")

conn.close()
