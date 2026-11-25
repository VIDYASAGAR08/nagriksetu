import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Student counts
total_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
unique_names = cur.execute("SELECT COUNT(DISTINCT student_name) FROM students").fetchone()[0]
print(f"Total students: {total_students}")
print(f"Unique student names: {unique_names}")
print(f"Duplicate student names count (total - unique): {total_students - unique_names}")

# Repeated names breakdown
repeated = cur.execute("""
    SELECT student_name, COUNT(*) as cnt, GROUP_CONCAT(DISTINCT s.school_name) as school_names, GROUP_CONCAT(DISTINCT st.school_id) as school_ids
    FROM students st
    JOIN schools s ON s.school_id = st.school_id
    GROUP BY student_name
    HAVING cnt > 1
    ORDER BY cnt DESC
""").fetchall()

print(f"\nNumber of name strings that appear more than once: {len(repeated)}")
print(f"Total student records with repeated names: {sum(r['cnt'] for r in repeated)}")
print(f"\nTop 25 Repeated Names:")
for r in repeated[:25]:
    print(f"  '{r['student_name']}': {r['cnt']} occurrences in [{r['school_ids']}] -> {r['school_names'][:80]}...")

# Check distribution across institutions
inst_students = cur.execute("""
    SELECT s.school_id, s.school_name, COUNT(st.student_id) as student_count
    FROM schools s
    LEFT JOIN students st ON st.school_id = s.school_id
    GROUP BY s.school_id
    ORDER BY student_count DESC
""").fetchall()

print(f"\nInstitutions and their student counts ({len(inst_students)} institutions):")
zero_student_insts = []
for r in inst_students:
    if r['student_count'] == 0:
        zero_student_insts.append(f"{r['school_id']} - {r['school_name']}")
    else:
        print(f"  [{r['school_id']}] {r['school_name']}: {r['student_count']} students")

print(f"\nInstitutions with 0 students ({len(zero_student_insts)}):")
for z in zero_student_insts:
    print(f"  {z}")

conn.close()
