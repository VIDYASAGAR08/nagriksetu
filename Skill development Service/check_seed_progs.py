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
    print("=== SEED / MIGRATION CHECK FOR PROGRAMMES 105-125 ===")
    cur.execute("SELECT id, code, title, skill_id, centre_id, created_at FROM training_programs WHERE id >= 105")
    rows = cur.fetchall()
    for r in rows:
        print(r)

    print("\n=== SKILLS 105-125 CREATION DATES / ACTIVE STATUS ===")
    cur.execute("SELECT id, code, name, category_name, active FROM skills WHERE id >= 100")
    srows = cur.fetchall()
    for sr in srows:
        print(sr)

conn.close()
