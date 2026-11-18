# -*- coding: utf-8 -*-
import requests
import json

base_url = "http://localhost:8001"
pid = "NS-FB8336A812DE468FB8E475443CF673EB" # Asha Sharma

# 1. Login staff
res = requests.post(f"{base_url}/auth/login", data={"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Record Attendance for 10 dates (9 present, 1 leave -> 90.0%)
dates = [
    ("2026-10-20", "present", "Present"),
    ("2026-10-21", "present", "Present"),
    ("2026-10-22", "present", "Active participation"),
    ("2026-10-23", "present", "Present"),
    ("2026-10-24", "present", "Present"),
    ("2026-10-27", "leave", "Family event leave approved"),
    ("2026-10-28", "present", "Present"),
    ("2026-10-29", "present", "Present"),
    ("2026-10-30", "present", "Present"),
    ("2026-10-31", "present", "Science exhibition"),
]

for d, st, rem in dates:
    payload = {
        "institution_id": "SCH001",
        "attendance_date": d,
        "subject_name": "General Instruction",
        "records": [{"permanent_student_id": pid, "status": st, "remarks": rem}]
    }
    r = requests.post(f"{base_url}/academic/attendance/batch", json=payload, headers=headers)
    assert r.status_code == 201

print("Logged 10 attendance sessions for Asha Sharma.")

# 3. Create or find Exam
exam_payload = {
    "institution_id": "SCH001",
    "exam_name": "Midterm Examination 2026",
    "academic_year": "2025-26",
    "exam_date": "2026-11-15",
    "standard": 5,
    "description": "State curriculum midterm comprehensive evaluation"
}
r = requests.post(f"{base_url}/academic/examinations", json=exam_payload, headers=headers)
exam_id = r.json().get("exam_id")

# 4. Record Results for 4 Subjects
results_payloads = [
    {"subject": "Kannada", "marks": 88.0, "max": 100.0},
    {"subject": "Mathematics", "marks": 94.0, "max": 100.0},
    {"subject": "English", "marks": 85.0, "max": 100.0},
    {"subject": "Science", "marks": 78.0, "max": 100.0},
    {"subject": "Social Science", "marks": 82.0, "max": 100.0},
]

for res_item in results_payloads:
    payload = {
        "institution_id": "SCH001",
        "exam_id": exam_id,
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "subject_name": res_item["subject"],
        "maximum_marks": res_item["max"],
        "records": [{"permanent_student_id": pid, "marks_obtained": res_item["marks"]}]
    }
    r = requests.post(f"{base_url}/academic/results/batch", json=payload, headers=headers)
    assert r.status_code == 201

print("Logged 5 subject marks for Asha Sharma.")

# 5. Check Performance
r = requests.get(f"{base_url}/academic/performance/{pid}", headers=headers)
perf = r.json()
print("Asha Attendance:", perf["attendance_summary"]["attendance_percentage"], "%")
print("Asha Results Count:", len(perf["academic_results"]))
print("Asha Subject Standing:", [(s["subject_name"], s["overall_grade"]) for s in perf["subject_performance"]])
