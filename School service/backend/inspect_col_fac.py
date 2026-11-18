import sqlite3
import json

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()

for r in c.execute("SELECT school_id, school_name, facilities_json FROM schools WHERE school_id LIKE 'COL%' LIMIT 2").fetchall():
    print(r[0], r[1])
    try:
        data = json.loads(r[2])
        print("Keys:", list(data.keys()) if isinstance(data, dict) else len(data))
    except Exception as e:
        print("Error:", e)
