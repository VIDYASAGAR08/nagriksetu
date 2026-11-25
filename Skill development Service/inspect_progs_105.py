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
    print("=== PROGRAMMES 105 to 125 ===")
    cur.execute("""
        SELECT tp.id, tp.code, tp.skill_id, tp.title, tp.centre_id, tc.name as centre_name, s.name as skill_name
        FROM training_programs tp
        LEFT JOIN training_centres tc ON tp.centre_id = tc.id
        LEFT JOIN skills s ON tp.skill_id = s.id
        WHERE tp.id >= 105
        ORDER BY tp.id
    """)
    progs = cur.fetchall()
    for p in progs:
        print(f"Prog ID: {p['id']} | Code: {p['code']} | Title: '{p['title']}' | Skill ID: {p['skill_id']} ('{p['skill_name']}') | Centre ID: {p['centre_id']} ({p['centre_name']})")

conn.close()
