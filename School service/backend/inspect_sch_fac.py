import sqlite3
import json

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()

for r in c.execute("SELECT school_id, school_name, facilities_json FROM schools WHERE school_id LIKE 'SCH%' LIMIT 3").fetchall():
    print(r[0], r[1], r[2])
