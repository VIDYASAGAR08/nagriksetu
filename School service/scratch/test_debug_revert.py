import json
import urllib.request
import urllib.error
from database import get_connection
from auth import create_access_token

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE school_id = 'SCH001'")
admin_sch001 = dict(cur.fetchone())
conn.close()

token = create_access_token(admin_sch001, school_id="SCH001")
print("Admin SCH001:", admin_sch001)

req = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps({"blood_group": "O+", "reason": "Testing revert"}).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
try:
    with urllib.request.urlopen(req) as resp:
        print("Success:", resp.status, resp.read().decode())
except urllib.error.HTTPError as he:
    print(f"Error {he.code}: {he.read().decode()}")
