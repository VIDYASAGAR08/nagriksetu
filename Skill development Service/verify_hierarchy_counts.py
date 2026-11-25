import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

print('--- Skills Per Main Category ---')
cur.execute('SELECT category_id, category_name, count(*) as cnt FROM skills GROUP BY category_id, category_name ORDER BY category_id')
for r in cur.fetchall():
    print(r)

print('\n--- Subcategories Check ---')
cur.execute('''
    SELECT c.name as category, sub.name as subcategory, count(s.id) as skill_cnt
    FROM subcategories sub
    JOIN categories c ON c.id = sub.category_id
    LEFT JOIN skills s ON s.subcategory_id = sub.id
    GROUP BY c.name, sub.id, sub.name
    ORDER BY c.id, sub.id
''')
all_subs = cur.fetchall()
print(f'Total subcategories: {len(all_subs)}')
min_skills = min(r['skill_cnt'] for r in all_subs)
print(f'Minimum skills in any subcategory: {min_skills}')
for r in all_subs:
    status = '[PASS]' if r['skill_cnt'] >= 5 else '[WARN]'
    print(f"{status} {r['category'][:25]:25} -> {r['subcategory'][:35]:35} : {r['skill_cnt']} skills")

conn.close()
