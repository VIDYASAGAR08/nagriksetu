import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute('SELECT id, code, name, category_id, category_name FROM skills WHERE id <= 104 ORDER BY id')
skills = cur.fetchall()
for s in skills:
    cid = str(s['category_id']) if s['category_id'] is not None else 'None'
    print(f"{s['id']:3d} | {s['code']} | {cid:4} | {s['category_name']:32} | {s['name']}")

conn.close()
