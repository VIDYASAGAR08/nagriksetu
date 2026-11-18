import requests
import json

base_url = "http://localhost:8001"

print("--- 1. Testing Valid Student Lookup (Ishaan Verma) ---")
res1 = requests.post(f"{base_url}/auth/student/lookup", json={"student_identifier": "NS-SCH019-STD06-166"})
print("Status:", res1.status_code)
print(json.dumps(res1.json(), indent=2))
assert res1.status_code == 200
data1 = res1.json()
assert data1["official_student_name"] == "Ishaan Verma"
assert data1["institution_id"] == "SCH019"
assert data1["standard"] == 6
assert data1["section"] == "C"

print("\n--- 2. Testing Student ID Not Found ---")
res2 = requests.post(f"{base_url}/auth/student/lookup", json={"student_identifier": "NS-SCH999-STD01-999"})
print("Status:", res2.status_code, "| Detail:", res2.json().get("detail"))
assert res2.status_code == 404
assert "Student ID not found" in res2.json().get("detail")

print("\n--- 3. Testing Student Account Already Activated ---")
res3 = requests.post(f"{base_url}/auth/student/lookup", json={"student_identifier": "SCH01125"})
print("Status:", res3.status_code, "| Detail:", res3.json().get("detail"))
assert res3.status_code == 400
assert "Student account already activated" in res3.json().get("detail")

print("\n--- 4. Testing Student Record Requires Institution Verification (Missing DOB) ---")
res4 = requests.post(f"{base_url}/auth/student/lookup", json={"student_identifier": "SCH01133"})
print("Status:", res4.status_code, "| Detail:", res4.json().get("detail"))
assert res4.status_code == 400
assert "Student record requires institution verification" in res4.json().get("detail")

print("\n--- 5. Testing Identity Verification Failure (Wrong DOB) ---")
res5 = requests.post(f"{base_url}/auth/student/register", json={
    "student_identifier": "NS-SCH019-STD06-166",
    "date_of_birth": "2015-01-01", # Wrong DOB! Actual is 2015-06-15
    "password": "Password@2026!",
    "confirm_password": "Password@2026!"
})
print("Status:", res5.status_code, "| Detail:", res5.json().get("detail"))
assert res5.status_code == 400
assert "Identity verification failed" in res5.json().get("detail")

print("\nALL 5 ERROR & LOOKUP CASES VERIFIED SUCCESSFULLY ON BACKEND!")
