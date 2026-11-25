import urllib.request
import urllib.parse
import json

# Login as parent using form data
login_data = urllib.parse.urlencode({"username": "parent.demo@example.com", "password": "Password@123"}).encode('utf-8')
req = urllib.request.Request("http://localhost:8000/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())["access_token"]

headers = {"Authorization": f"Bearer {token}"}
url = "http://localhost:8000/parent/lookup-by-student-id?student_id=SCH01125"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response body:", e.read().decode())
