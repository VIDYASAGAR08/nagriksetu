import pymysql

conn = pymysql.connect(host="127.0.0.1", port=3308, user="nagriksetu_skill", password="skill-app-pass-2026", database="skill_db")
cur = conn.cursor(pymysql.cursors.DictCursor)

print("--- 1. Check accounts.student_id column & index ---")
cur.execute("SHOW COLUMNS FROM accounts LIKE 'student_id'")
print("Column:", cur.fetchall())

cur.execute("SHOW INDEX FROM accounts WHERE Column_name = 'student_id'")
print("Index:", cur.fetchall())

print("\n--- 2. Citizens with multiple enrolments ---")
cur.execute("""
    SELECT a.id AS account_id, a.email, a.citizen_ref, a.student_id AS account_student_id, COUNT(e.id) AS enrolment_count,
           GROUP_CONCAT(e.student_id) AS enrolment_student_ids,
           COUNT(DISTINCT e.student_id) AS distinct_enrolment_student_ids
    FROM accounts a
    JOIN enrollments e ON e.citizen_ref = a.citizen_ref
    WHERE e.status = 'ENROLLED'
    GROUP BY a.id, a.email, a.citizen_ref, a.student_id
    HAVING enrolment_count > 1
""")
multi_enrolled = cur.fetchall()
print("Multi-enrolled citizens count:", len(multi_enrolled))
for row in multi_enrolled:
    print(row)

print("\n--- 3. Check for any non-enrolled citizen with a student_id ---")
cur.execute("""
    SELECT a.id, a.email, a.citizen_ref, a.student_id 
    FROM accounts a
    LEFT JOIN enrollments e ON e.citizen_ref = a.citizen_ref AND e.status = 'ENROLLED'
    WHERE a.student_id IS NOT NULL AND e.id IS NULL
""")
invalid_students = cur.fetchall()
print("Non-enrolled citizens with student_id:", invalid_students)

print("\n--- 4. Check for shared student_ids across different accounts ---")
cur.execute("""
    SELECT student_id, COUNT(*) as cnt 
    FROM accounts 
    WHERE student_id IS NOT NULL 
    GROUP BY student_id 
    HAVING cnt > 1
""")
shared_ids = cur.fetchall()
print("Shared student_ids across accounts:", shared_ids)

print("\n--- 5. Check if any enrolment student_id mismatches accounts.student_id ---")
cur.execute("""
    SELECT e.id as enrolment_id, e.code, e.citizen_ref, e.student_id as enr_student_id, a.student_id as acc_student_id
    FROM enrollments e
    JOIN accounts a ON e.citizen_ref = a.citizen_ref
    WHERE e.status = 'ENROLLED' AND e.student_id != a.student_id
""")
mismatches = cur.fetchall()
print("Enrolment vs Account student_id mismatches:", mismatches)

print("\n--- 6. All ENROLLED records and their student_ids ---")
cur.execute("""
    SELECT e.id, e.code, e.citizen_ref, e.citizen_name, e.student_id, a.student_id as acc_student_id
    FROM enrollments e
    JOIN accounts a ON e.citizen_ref = a.citizen_ref
    WHERE e.status = 'ENROLLED'
    ORDER BY e.id
""")
all_enrolled = cur.fetchall()
print(f"Total ENROLLED records: {len(all_enrolled)}")
for r in all_enrolled[:5]:
    print(r)

conn.close()
