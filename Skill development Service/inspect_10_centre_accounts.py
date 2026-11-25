import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db'
)

cur = conn.cursor(pymysql.cursors.DictCursor)
target_account_ids = [97, 94, 96, 95, 139, 140, 135, 136, 137, 138]

query = f"""
SELECT a.id as account_id, a.email, a.role, a.active, a.centre_id,
       tc.id as tc_id, tc.code as tc_code, tc.name as tc_name
FROM accounts a
JOIN training_centres tc ON a.centre_id = tc.id
WHERE a.id IN ({','.join(map(str, target_account_ids))})
ORDER BY tc.id
"""

cur.execute(query)
rows = cur.fetchall()

print(f"Found {len(rows)} matching accounts:")
for r in rows:
    aid = r['account_id']
    cid = r['centre_id']
    code = r['tc_code']
    email = r['email']
    name = r['tc_name']
    print(f"Account {aid:3} | Centre {cid:2} | Code {code:10} | Email: {email:36} | Name: {name}")
