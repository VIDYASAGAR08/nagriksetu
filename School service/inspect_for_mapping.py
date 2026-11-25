import sqlite3
import json

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- BASIC COUNTS ---")
cur.execute("SELECT count(*) FROM schools")
total_schools = cur.fetchone()[0]
print("Total schools/institutions:", total_schools)

cur.execute("SELECT count(*) FROM students")
total_students = cur.fetchone()[0]
print("Total students:", total_students)

cur.execute("SELECT count(DISTINCT student_id), count(DISTINCT permanent_student_id) FROM students")
row = cur.fetchone()
print(f"Unique student_id: {row[0]}, Unique permanent_student_id: {row[1]}")

cur.execute("SELECT count(*) FROM enrollments")
total_enrollments = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM enrollments WHERE LOWER(enrollment_status) = 'active'")
active_enrollments = cur.fetchone()[0]
print(f"Total enrollments: {total_enrollments}, Active enrollments: {active_enrollments}")

cur.execute("SELECT count(*) FROM collegiate_enrollments")
total_collegiate = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM collegiate_enrollments WHERE LOWER(enrollment_status) = 'active'")
active_collegiate = cur.fetchone()[0]
print(f"Total collegiate_enrollments: {total_collegiate}, Active collegiate: {active_collegiate}")

print("\n--- INSTITUTIONS LIST (31) ---")
cur.execute("SELECT school_id, school_name, school_type, category, district, state FROM schools ORDER BY school_id")
schools = [dict(r) for r in cur.fetchall()]
for s in schools:
    print(f"{s['school_id']:<10} | {s['school_name'][:40]:<40} | {s['school_type']:<20} | {s['category']:<20} | {s['district']}, {s['state']}")

print("\n--- STUDENT ENROLLMENT MAPPINGS PER INSTITUTION ---")
# Check students count per school_id directly from students table
cur.execute("""
SELECT 
    s.school_id,
    sc.school_name,
    sc.school_type,
    count(s.permanent_student_id) as student_count
FROM students s
LEFT JOIN schools sc ON s.school_id = sc.school_id
GROUP BY s.school_id, sc.school_name, sc.school_type
ORDER BY s.school_id
""")
student_counts = cur.fetchall()
total_mapped_students = 0
for m in student_counts:
    print(f"{m['school_id']:<10} | {str(m['school_name'])[:40]:<40} | {str(m['school_type']):<20} | {m['student_count']}")
    total_mapped_students += m['student_count']
print(f"Total mapped students: {total_mapped_students}")

print("\n--- INTEGRITY CHECKS ---")
# 1. Unmapped students
cur.execute("SELECT count(*) FROM students WHERE school_id IS NULL OR TRIM(school_id) = ''")
unmapped = cur.fetchone()[0]
print("Students with NULL/empty school_id:", unmapped)

# 2. Invalid school references
cur.execute("SELECT count(*) FROM students WHERE school_id NOT IN (SELECT school_id FROM schools)")
invalid_schools = cur.fetchone()[0]
print("Students with invalid school_id reference:", invalid_schools)

# 3. Duplicate student_id or permanent_student_id
cur.execute("SELECT student_id, count(*) FROM students GROUP BY student_id HAVING count(*) > 1")
dup_sid = cur.fetchall()
print("Duplicate student_ids:", len(dup_sid))

cur.execute("SELECT permanent_student_id, count(*) FROM students GROUP BY permanent_student_id HAVING count(*) > 1")
dup_psid = cur.fetchall()
print("Duplicate permanent_student_ids:", len(dup_psid))

# 4. Check enrollments per student
cur.execute("""
SELECT permanent_student_id, count(*) 
FROM enrollments 
GROUP BY permanent_student_id 
HAVING count(*) > 1
""")
multi_enroll = cur.fetchall()
print("Students with multiple enrollment records in 'enrollments':", len(multi_enroll))

cur.execute("""
SELECT permanent_student_id, count(DISTINCT school_id) 
FROM enrollments 
GROUP BY permanent_student_id 
HAVING count(DISTINCT school_id) > 1
""")
multi_school_enroll = cur.fetchall()
print("Students enrolled in multiple institutions across 'enrollments':", len(multi_school_enroll))

# 5. Check if every student has an enrollment record
cur.execute("SELECT count(*) FROM students WHERE permanent_student_id NOT IN (SELECT permanent_student_id FROM enrollments)")
no_enrollment = cur.fetchone()[0]
print("Students with NO record in 'enrollments':", no_enrollment)

# 6. Check collegiate_enrollments vs students
cur.execute("SELECT count(*) FROM collegiate_enrollments ce JOIN students s ON ce.permanent_student_id = s.permanent_student_id")
colleg_matches = cur.fetchone()[0]
print("Collegiate enrollments matching students:", colleg_matches)

# 7. Check active enrollments per school
cur.execute("""
SELECT 
    sc.school_id,
    sc.school_name,
    count(e.enrollment_id) as total_enroll,
    SUM(CASE WHEN LOWER(e.enrollment_status) = 'active' THEN 1 ELSE 0 END) as active_enroll
FROM schools sc
LEFT JOIN enrollments e ON sc.school_id = e.school_id
GROUP BY sc.school_id, sc.school_name
ORDER BY sc.school_id
""")
for r in cur.fetchall():
    print(f"{r['school_id']:<10} | {r['school_name'][:35]:<35} | Total: {r['total_enroll']} | Active: {r['active_enroll']}")

# 8. Check academic programs table and how they link
print("\n--- ACADEMIC PROGRAMS CHECK ---")
cur.execute("SELECT program_id, institution_id, program_name, degree_type, discipline_or_stream, faculty_name, department_name FROM academic_programs LIMIT 10")
for r in cur.fetchall():
    print(dict(r))

# 9. Check what stream, subject_combination, program details exist in enrollments or collegiate_enrollments
cur.execute("SELECT stream, count(*) FROM enrollments GROUP BY stream")
print("\nStreams in enrollments:", [dict(r) for r in cur.fetchall()])

cur.execute("SELECT DISTINCT academic_year FROM enrollments")
print("Academic years in enrollments:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT DISTINCT enrollment_status FROM enrollments")
print("Enrollment statuses in enrollments:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT DISTINCT enrollment_status FROM students")
print("Enrollment statuses in students table:", [r[0] for r in cur.fetchall()])
