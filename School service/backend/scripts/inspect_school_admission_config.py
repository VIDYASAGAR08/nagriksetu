import sqlite3
import urllib.request
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

schools_15 = [f"SCH{i:03d}" for i in range(1, 11)] + [f"SCH{i:03d}" for i in range(16, 21)]
print("Checking all 15 schools:", schools_15)

for sid in schools_15:
    s = c.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (sid,)).fetchone()
    progs = c.execute("SELECT program_id, education_level, program_name FROM academic_programs WHERE institution_id = ?", (sid,)).fetchall()
    prog_levels = set(p['education_level'] for p in progs)
    print(f"{sid} | Name: {s['school_name'][:30]} | Cat: {s['category']} | Type: {s['school_type']} | Prog levels: {prog_levels}")

conn.close()

# Also test API form-config for SCH001
url = "http://localhost:8001/admissions/form-config/SCH001"
req = urllib.request.urlopen(url)
data = json.loads(req.read().decode())
print("\nForm config for SCH001:")
print(" offered_levels:", data.get("offered_levels"))
print(" has_school_offerings:", data.get("has_school_offerings"))
print(" pu_config is None?:", data.get("pu_config") is None)
if data.get("pu_config"):
    print(" pu_config:", data.get("pu_config"))
