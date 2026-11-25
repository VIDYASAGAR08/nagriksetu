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

    # 2. Distinct skills that have at least one programme
    cur.execute("""
        SELECT COUNT(DISTINCT skill_id) as cnt
        FROM training_programs
        WHERE skill_id IS NOT NULL
    """)
    skills_with_progs = cur.fetchone()["cnt"]

    # 3. Active skills with programmes vs without programmes
    cur.execute("""
        SELECT COUNT(s.id) as cnt
        FROM skills s
        WHERE s.active = 1
        AND s.id IN (SELECT DISTINCT skill_id FROM training_programs WHERE skill_id IS NOT NULL)
    """)
    active_skills_with_progs = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COUNT(s.id) as cnt
        FROM skills s
        WHERE s.active = 1
        AND s.id NOT IN (SELECT DISTINCT skill_id FROM training_programs WHERE skill_id IS NOT NULL)
    """)
    active_skills_without_progs = cur.fetchone()["cnt"]

    # 4. Check programme-to-centre relationship integrity
    cur.execute("""
        SELECT COUNT(*) as cnt
        FROM training_programs
        WHERE centre_id IS NULL OR centre_id NOT IN (SELECT id FROM training_centres)
    """)
    orphaned_prog_centres = cur.fetchone()["cnt"]

    # 5. Check programme-to-batch relationship integrity
    cur.execute("SELECT COUNT(*) as cnt FROM batches")
    total_batches = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COUNT(*) as cnt
        FROM batches
        WHERE program_id IS NULL OR program_id NOT IN (SELECT id FROM training_programs)
    """)
    orphaned_batches = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COUNT(DISTINCT program_id) as cnt FROM batches WHERE program_id IS NOT NULL
    """)
    progs_with_batches = cur.fetchone()["cnt"]

    print(f"Total training programs in DB: {total_progs}")
    print(f"Distinct skills associated with programs: {skills_with_progs}")
    print(f"Active skills WITH live training programs: {active_skills_with_progs}")
    print(f"Active skills WITHOUT live training programs: {active_skills_without_progs}")
    print(f"Orphaned program-to-centre links: {orphaned_prog_centres}")
    print(f"Total batches in DB: {total_batches}")
    print(f"Programs with configured batches: {progs_with_batches}")
    print(f"Orphaned batches: {orphaned_batches}")

    # Check enrolments / application flow for skills without programs
    print("\nSample skills WITHOUT training programs (first 10):")
    cur.execute("""
        SELECT s.id, s.code, s.name, s.category_name, s.subcategory_name
        FROM skills s
        WHERE s.active = 1
        AND s.id NOT IN (SELECT DISTINCT skill_id FROM training_programs WHERE skill_id IS NOT NULL)
        LIMIT 10
    """)
    for s in cur.fetchall():
        print(f"  [{s['code']}] {s['name']} | {s['category_name']} -> {s['subcategory_name']}")

conn.close()
