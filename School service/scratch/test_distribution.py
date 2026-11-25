import sqlite3
import csv

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get all institutions
cur.execute("SELECT school_id, school_name, school_type, category, district FROM schools ORDER BY school_id")
institutions = [dict(r) for r in cur.fetchall()]

# Get current student counts per institution
cur.execute("SELECT school_id, COUNT(*) as cnt FROM students GROUP BY school_id")
current_counts = {r["school_id"]: r["cnt"] for r in cur.fetchall()}

# Get capacities from program_sections
cur.execute("SELECT institution_id, SUM(capacity) as cap FROM program_sections GROUP BY institution_id")
capacities = {r["institution_id"]: r["cap"] for r in cur.fetchall()}

print("=== INSTITUTION CAPACITY & DISTRIBUTION AUDIT ===")
for inst in institutions:
    sid = inst["school_id"]
    curr = current_counts.get(sid, 0)
    cap = capacities.get(sid, 0)
    print(f"{sid}: curr={curr}, cap={cap}, type={inst['school_type']}, dist={inst['district']}")

conn.close()
