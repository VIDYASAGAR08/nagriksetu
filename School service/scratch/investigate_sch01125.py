import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

print("--- Looking up SCH01125 in students ---")
stu_sch01125 = c.execute("SELECT * FROM students WHERE student_id = 'SCH01125'").fetchall()
for s in stu_sch01125:
    print("Student row:", s)

print("\n--- Looking up SCH01125 in users ---")
user_sch01125 = c.execute("SELECT * FROM users WHERE student_id = 'SCH01125'").fetchall()
for u in user_sch01125:
    print("User row:", u)

print("\n--- Looking up 'Asha Sharma' in students ---")
asha_students = c.execute("SELECT student_id, student_name, school_id, standard, section, permanent_student_id FROM students WHERE student_name = 'Asha Sharma'").fetchall()
for s in asha_students:
    print("Asha student:", s)

print("\n--- Looking up 'Asha' in users ---")
asha_users = c.execute("SELECT user_id, email, phone, role, student_id, permanent_student_id, full_name FROM users WHERE full_name LIKE '%Asha%' OR email LIKE '%asha%'").fetchall()
for u in asha_users:
    print("Asha user:", u)

print("\n--- Looking up 'Raju%' in students ---")
raju_students = c.execute("SELECT student_id, student_name, school_id, standard, section, permanent_student_id FROM students WHERE student_name LIKE '%Raju%'").fetchall()
print(f"Total students with name like Raju: {len(raju_students)}")
for s in raju_students:
    print("Raju student:", s)

print("\n--- Looking up 'Raju%' in users ---")
raju_users = c.execute("SELECT user_id, email, phone, role, student_id, permanent_student_id, full_name FROM users WHERE full_name LIKE '%Raju%' OR email LIKE '%raju%'").fetchall()
print(f"Total users with name like Raju: {len(raju_users)}")
for u in raju_users:
    print("Raju user:", u)

print("\n--- Looking up audit_logs or linking_requests for Raju ---")
logs = c.execute("SELECT * FROM audit_logs WHERE payload LIKE '%Raju%' OR payload LIKE '%SCH01125%'").fetchall()
print(f"Audit logs count: {len(logs)}")
for l in logs:
    print("Audit log:", l)

conn.close()
