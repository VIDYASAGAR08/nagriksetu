import sqlite3
import json
import urllib.request
import urllib.parse

# 1. Get sample students from DB
conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

# School student
c.execute("SELECT student_id, student_name FROM students WHERE school_id = 'SCH001' AND standard = 1 LIMIT 1")
sch_student = c.fetchone()

# 1st PUC PCMB student
c.execute("SELECT student_id, student_name, subject_combination, stream FROM students WHERE school_id = 'SCH011' AND standard = 11 AND subject_combination = 'PCMB' LIMIT 1")
pcmb_student = c.fetchone()

# 1st PUC PCMC student
c.execute("SELECT student_id, student_name, subject_combination, stream FROM students WHERE school_id = 'SCH011' AND standard = 11 AND subject_combination = 'PCMC' LIMIT 1")
pcmc_student = c.fetchone()

# 2nd PUC Commerce student
c.execute("SELECT student_id, student_name, subject_combination, stream FROM students WHERE school_id = 'SCH011' AND standard = 12 AND stream = 'Commerce' LIMIT 1")
comm_student = c.fetchone()

# Engineering student
c.execute("SELECT student_id, student_name, degree, branch, department FROM students WHERE school_id = 'COL003' LIMIT 1")
eng_student = c.fetchone()

conn.close()

print("Sample students selected for testing:")
print("  School student:", sch_student)
print("  PCMB 1st PUC student:", pcmb_student)
print("  PCMC 1st PUC student:", pcmc_student)
print("  Commerce 2nd PUC student:", comm_student)
print("  Engineering student:", eng_student)

# 2. Get a valid parent token
login_data = json.dumps({"username": "parent.demo@example.com", "password": "Password@123"}).encode('utf-8')
req = urllib.request.Request("http://localhost:8000/auth/login", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 3. Test lookup for each student
for label, stu in [
    ("School Student", sch_student[0]),
    ("PCMB 1st PUC Student", pcmb_student[0]),
    ("PCMC 1st PUC Student", pcmc_student[0]),
    ("Commerce 2nd PUC Student", comm_student[0]),
    ("Engineering Student", eng_student[0])
]:
    url = f"http://localhost:8000/parent/lookup-by-student-id?student_id={urllib.parse.quote(stu)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"\n==========================================")
        print(f"LOOKUP RESULT: {label} ({stu})")
        print(f"==========================================")
        print(f"  Name: {res.get('student_full_name')}")
        print(f"  Institution: {res.get('institution_name')} ({res.get('institution_id')})")
        print(f"  Tier: {res.get('institution_tier')}")
        print(f"  Class / Standard: {res.get('class_or_standard')}")
        print(f"  Board: {res.get('board')}")
        print(f"  PUC Year: {res.get('puc_year')}")
        print(f"  Stream: {res.get('stream')}")
        print(f"  Combination: {res.get('subject_combination')}")
        print(f"  Degree: {res.get('degree')}")
        print(f"  Branch: {res.get('branch')}")
        print(f"  Department: {res.get('department')}")
        print(f"  Semester: {res.get('semester')}")
        print(f"  Academic Year: {res.get('academic_year')}")
