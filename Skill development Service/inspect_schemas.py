import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

for table in ['categories', 'skills', 'training_programs', 'training_centres', 'batches', 'enrollments']:
    cur.execute(f'DESCRIBE {table}')
    cols = [f"{r['Field']} ({r['Type']})" for r in cur.fetchall()]
    print(f'=== {table} ===\n' + ', '.join(cols) + '\n')

print('--- Existing Categories ---')
cur.execute('SELECT * FROM categories')
for c in cur.fetchall():
    print(c)

print('\n--- Skills Sample & Count ---')
cur.execute('SELECT count(*) as cnt FROM skills')
print('Total skills:', cur.fetchone()['cnt'])
cur.execute('SELECT id, code, name, category_id, category_name FROM skills LIMIT 10')
for s in cur.fetchall():
    print(s)

print('\n--- Programs Sample & Count ---')
cur.execute('SELECT count(*) as cnt FROM training_programs')
print('Total programs:', cur.fetchone()['cnt'])
cur.execute('SELECT id, code, title, skill_id, centre_id, trainer_id FROM training_programs LIMIT 5')
for p in cur.fetchall():
    print(p)

print('\n--- Centres Sample & Count ---')
cur.execute('SELECT count(*) as cnt FROM training_centres')
print('Total centres:', cur.fetchone()['cnt'])
cur.execute('SELECT id, code, name, district, approval_status, active FROM training_centres LIMIT 5')
for c in cur.fetchall():
    print(c)

conn.close()
