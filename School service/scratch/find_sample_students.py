import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

def get_name_sort_key(name):
    clean = (name or '').strip()
    parts = clean.split()
    first_name = parts[0].lower() if parts else ''
    full_name = clean.lower()
    return (first_name, full_name)

sch001_students = c.execute(
    "SELECT student_id, student_name, permanent_student_id FROM students WHERE school_id = 'SCH001'"
).fetchall()

sorted_sch001 = sorted(sch001_students, key=lambda s: get_name_sort_key(s[1]))

for i, s in enumerate(sorted_sch001, 1):
    if s[1] == 'Asha Sharma':
        print(f"Asha Sharma: Seq {i:3d} -> New ID: SCH001{i:03d} (Old: {s[0]}, Perm: {s[2]})")
    if s[1] == 'Kiran Kumar':
        print(f"Kiran Kumar: Seq {i:3d} -> New ID: SCH001{i:03d} (Old: {s[0]}, Perm: {s[2]})")

conn.close()
