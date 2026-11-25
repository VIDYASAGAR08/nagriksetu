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
    # 1. Total skills count
    cur.execute("SELECT COUNT(*) as cnt FROM skills")
    total_skills = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE active = 1")
    active_skills = cur.fetchone()["cnt"]

    # 2. Check existing 104 skills (codes SKL-0001 to SKL-0104)
    cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE id <= 104")
    preserved_104 = cur.fetchone()["cnt"]

    # 3. Newly added skills
    cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE id > 104")
    new_skills = cur.fetchone()["cnt"]

    # Check IDs range and code patterns
    cur.execute("SELECT MIN(id) as min_id, MAX(id) as max_id FROM skills")
    id_range = cur.fetchone()

    # Check for duplicates by name or code
    cur.execute("SELECT name, COUNT(*) as cnt FROM skills GROUP BY name HAVING cnt > 1")
    dup_names = cur.fetchall()

    cur.execute("SELECT code, COUNT(*) as cnt FROM skills GROUP BY code HAVING cnt > 1")
    dup_codes = cur.fetchall()

    print(f"Total skills in DB: {total_skills}")
    print(f"Active skills: {active_skills}")
    print(f"Skills with id <= 104: {preserved_104}")
    print(f"Skills with id > 104: {new_skills}")
    print(f"ID Range: {id_range['min_id']} to {id_range['max_id']}")
    print(f"Duplicate names ({len(dup_names)}): {dup_names}")
    print(f"Duplicate codes ({len(dup_codes)}): {dup_codes}")

    # Reconcile why 208 was in admin-catalogue vs 228
    # Let's check categories and subcategories count of skills
    cur.execute("""
        SELECT c.id, c.name, COUNT(s.id) as skill_cnt
        FROM categories c
        LEFT JOIN skills s ON s.category_id = c.id
        GROUP BY c.id, c.name
    """)
    cat_counts = cur.fetchall()
    print("\nSkills per Category (by category_id):")
    for cc in cat_counts:
        print(f"  Cat {cc['id']}: {cc['name']} -> {cc['skill_cnt']} skills")

    cur.execute("""
        SELECT c.id, c.name, COUNT(s.id) as skill_cnt
        FROM categories c
        LEFT JOIN skills s ON s.category_name = c.name
        GROUP BY c.id, c.name
    """)
    cat_name_counts = cur.fetchall()
    print("\nSkills per Category (by category_name):")
    for cc in cat_name_counts:
        print(f"  Cat {cc['id']}: {cc['name']} -> {cc['skill_cnt']} skills")

    # Skills without subcategory or category
    cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE subcategory_id IS NULL")
    no_subcat = cur.fetchone()["cnt"]
    print(f"\nSkills with subcategory_id IS NULL: {no_subcat}")

    cur.execute("SELECT COUNT(*) as cnt FROM skills WHERE category_id IS NULL")
    no_cat = cur.fetchone()["cnt"]
    print(f"Skills with category_id IS NULL: {no_cat}")

    # Let's check skills with category_id != corresponding category for subcategory
    cur.execute("""
        SELECT s.id, s.code, s.name, s.category_id, s.category_name, s.subcategory_id, s.subcategory_name, sub.category_id as sub_cat_id
        FROM skills s
        LEFT JOIN subcategories sub ON s.subcategory_id = sub.id
        WHERE s.category_id != sub.category_id
    """)
    mismatched = cur.fetchall()
    print(f"Skills where skill.category_id != subcategory.category_id: {len(mismatched)}")

conn.close()
