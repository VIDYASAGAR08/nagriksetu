import sqlite3
import re

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("=" * 65)
print("1. EXISTING STUDENT IDS AUDIT")
print("=" * 65)

total_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
unique_ids = c.execute("SELECT COUNT(DISTINCT student_id) FROM students").fetchone()[0]
null_ids = c.execute("SELECT COUNT(*) FROM students WHERE student_id IS NULL OR student_id = ''").fetchone()[0]
print(f"Total students: {total_students}")
print(f"Unique student_ids: {unique_ids}")
print(f"Null / Empty student_ids: {null_ids}")

# Check formats of existing IDs
existing_patterns = {}
for (sid,) in c.execute("SELECT student_id FROM students").fetchall():
    match = re.match(r"^([A-Z0-9]+)-([A-Z0-9]+)-([0-9]+)$", sid)
    if match:
        pat = "PREFIX-STD-NUM"
    else:
        pat = "OTHER"
    existing_patterns[pat] = existing_patterns.get(pat, 0) + 1

print(f"Existing ID patterns: {existing_patterns}")

# Check duplicate student IDs
duplicates = c.execute(
    "SELECT student_id, COUNT(*) FROM students GROUP BY student_id HAVING COUNT(*) > 1"
).fetchall()
print(f"Duplicate student IDs count: {len(duplicates)}")

# Check duplicate student names within same institution
same_inst_dups = c.execute(
    "SELECT school_id, student_name, COUNT(*) FROM students GROUP BY school_id, student_name HAVING COUNT(*) > 1 LIMIT 10"
).fetchall()
print(f"Sample duplicate student names in same institution: {len(same_inst_dups)}")
for d in same_inst_dups:
    print(f"  {d[0]}: '{d[1]}' appears {d[2]} times")

print("\n" + "=" * 65)
print("2. INSTITUTION-WISE STUDENT DISTRIBUTION")
print("=" * 65)

schools = c.execute("SELECT school_id, school_name, school_type FROM schools ORDER BY school_id").fetchall()
inst_counts = {}
for s in schools:
    cnt = c.execute("SELECT COUNT(*) FROM students WHERE school_id = ?", (s[0],)).fetchone()[0]
    inst_counts[s[0]] = cnt
    print(f"{s[0]} ({s[1]} - {s[2]}): {cnt} students")

print("\n" + "=" * 65)
print("3. SORTING SIMULATION & ID GENERATION PREVIEW")
print("=" * 65)

# Simulate sorting for SCH001:
# Sort students alphabetically by first name (A–Z).
# If first names match, sort by complete student name.
# Assign sequential numbers starting from 001.

def get_name_sort_key(name):
    clean = (name or "").strip()
    parts = clean.split()
    first_name = parts[0].lower() if parts else ""
    full_name = clean.lower()
    return (first_name, full_name)

sch001_students = c.execute(
    "SELECT student_id, student_name, permanent_student_id FROM students WHERE school_id = 'SCH001'"
).fetchall()

sorted_sch001 = sorted(sch001_students, key=lambda s: get_name_sort_key(s[1]))

print(f"Total students in SCH001: {len(sorted_sch001)}")
print("First 15 students sorted by first name, then full name:")
for i, s in enumerate(sorted_sch001[:15], 1):
    new_id_exact = f"SCH001{i:03d}"
    new_id_alt = f"SCH01{i:03d}"
    print(f"  {i:3d}. Name: {s[1]:25} | Old ID: {s[0]:18} | New (Exact): {new_id_exact:10} | New (Alt): {new_id_alt:9}")

print("\nDuplicate First Names Handling Sample at SCH001:")
first_name_groups = {}
for s in sorted_sch001:
    fn = s[1].strip().split()[0].lower()
    first_name_groups.setdefault(fn, []).append(s)

dup_fn = {k: v for k, v in first_name_groups.items() if len(v) > 1}
print(f"First names with multiple students at SCH001: {len(dup_fn)} distinct first names")
# Show top 3 first names with ties
for fn in list(dup_fn.keys())[:3]:
    print(f"Group '{fn.title()}':")
    for s in dup_fn[fn][:5]:
        print(f"    - {s[1]}")

print("\n" + "=" * 65)
print("4. CHECK HIGH CAPACITY INSTITUTION (SCH011: 2400 STUDENTS)")
print("=" * 65)
sch011_students = c.execute(
    "SELECT student_id, student_name, permanent_student_id FROM students WHERE school_id = 'SCH011'"
).fetchall()
sorted_sch011 = sorted(sch011_students, key=lambda s: get_name_sort_key(s[1]))
print(f"SCH011 student 1:    Name: {sorted_sch011[0][1]} -> SCH011001 (or SCH11001)")
print(f"SCH011 student 999:  Name: {sorted_sch011[998][1]} -> SCH011999 (or SCH11999)")
print(f"SCH011 student 1000: Name: {sorted_sch011[999][1]} -> SCH0111000 (or SCH111000)")
print(f"SCH011 student 2400: Name: {sorted_sch011[2399][1]} -> SCH0112400 (or SCH112400)")

conn.close()
