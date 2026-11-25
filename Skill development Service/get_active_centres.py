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
    cur.execute("SELECT id, code, name, district, active FROM training_centres WHERE active = 1 ORDER BY id")
    active_centres = cur.fetchall()
    print("Active centres count:", len(active_centres))
    for c in active_centres:
        print(f"  ID: {c['id']}, Code: {c['code']}, Name: {c['name']}, District: {c['district']}")

conn.close()
