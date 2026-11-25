import sqlite3
import csv
from collections import Counter

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check flagged counts
cur.execute("""
    SELECT school_id, standard, COUNT(*)
    FROM students
    WHERE review_flag IS NOT NULL
    GROUP BY school_id, standard
    ORDER BY school_id, standard
""")
rows = cur.fetchall()
print(f"Total flagged student cohorts: {len(rows)}")
for r in rows[:15]:
    print(dict(r))

conn.close()
