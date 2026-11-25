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
    cur.execute("SELECT id, code, name, category_name, active FROM skills WHERE active = 0")
    inactives = cur.fetchall()
    print("Inactive skills count:", len(inactives))
    for s in inactives:
        print(f"  ID: {s['id']}, Code: {s['code']}, Name: {s['name']}, Cat: {s['category_name']}")

    # Let's see active skills count per category
    cur.execute("""
        SELECT c.id, c.name, 
               COUNT(s.id) as total_cnt,
               SUM(CASE WHEN s.active = 1 THEN 1 ELSE 0 END) as active_cnt
        FROM categories c
        LEFT JOIN skills s ON s.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY c.id
    """)
    rows = cur.fetchall()
    print("\nTotal vs Active Skills per Category:")
    for r in rows:
        print(f"  Cat {r['id']} ({r['name']}): Total={r['total_cnt']}, Active={r['active_cnt']}")

conn.close()
