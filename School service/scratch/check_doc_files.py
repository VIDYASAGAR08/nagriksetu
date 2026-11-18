import sqlite3
import os

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

docs = cur.execute('SELECT * FROM admission_documents WHERE application_id = ?', ('APP-2026-SCH019-6ED0FE',)).fetchall()
for d in docs:
    p = d['file_path']
    local_p = p.replace('/app/', 'C:/Users/callm/nagriksetu/backend/').replace('/', os.sep)
    print(d['document_type'], '|', d['file_name'])
    print('  Path in DB:', p)
    print('  Local Windows path:', local_p, '| Exists:', os.path.exists(local_p))
