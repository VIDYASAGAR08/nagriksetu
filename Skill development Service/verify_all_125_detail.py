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
    cur.execute("""
        SELECT tc.id as centre_id, tc.code as centre_code, tc.name as centre_name,
               tp.id as program_id, tp.code as program_code, tp.title as program_title,
               s.code as skill_code, s.name as skill_name,
               COUNT(b.id) as batch_count
        FROM training_centres tc
        JOIN training_programs tp ON tc.id = tp.centre_id
        LEFT JOIN skills s ON tp.skill_id = s.id
        LEFT JOIN batches b ON tp.id = b.program_id
        WHERE tc.active = 1
        GROUP BY tc.id, tc.code, tc.name, tp.id, tp.code, tp.title, s.code, s.name
        ORDER BY tc.id, tp.id
    """)
    rows = cur.fetchall()
    
    current_cid = None
    for r in rows:
        if r['centre_id'] != current_cid:
            current_cid = r['centre_id']
            print(f"\n==========================================")
            print(f"CENTRE {r['centre_id']} ({r['centre_code']}): {r['centre_name']}")
            print(f"==========================================")
        print(f"  Prog #{r['program_id']} ({r['program_code']}): '{r['program_title']}' | Skill: {r['skill_code']} ('{r['skill_name']}') | Batches: {r['batch_count']}")

conn.close()
