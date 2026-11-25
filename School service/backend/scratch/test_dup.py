import urllib.request
import urllib.parse
import json
import sqlite3

BASE_URL = "http://127.0.0.1:8001"

dup_email = "ambiguous.test.citizen@karnataka.gov.in"
dup_user1 = "test-dup-user-1"
dup_user2 = "test-dup-user-2"
dup_guardian2 = "test-dup-guardian-2"

conn = sqlite3.connect("C:/Users/callm/nagriksetu/backend/data/nagriksetu.db")
conn.execute("DELETE FROM guardians WHERE guardian_id = ?", (dup_guardian2,))
conn.execute("DELETE FROM users WHERE user_id IN (?, ?)", (dup_user1, dup_user2))
conn.execute("INSERT INTO users (user_id, email, phone, password_hash, role, is_active, full_name) VALUES (?, ?, '9111111111', 'hash1', 'parent', 1, 'Dup One')", (dup_user1, dup_email))
conn.execute("INSERT INTO users (user_id, email, phone, password_hash, role, is_active, full_name) VALUES (?, NULL, '9222222222', 'hash2', 'parent', 1, 'Dup Two')", (dup_user2,))
conn.execute("INSERT INTO guardians (guardian_id, user_id, full_name, email, phone, relationship) VALUES (?, ?, 'Dup Two Guardian', ?, '9222222222', 'Parent')", (dup_guardian2, dup_user2, dup_email))
conn.commit()
conn.close() # Released lock!

url = f"{BASE_URL}/auth/login"
data = urllib.parse.urlencode({"username": dup_email, "password": "AnyPassword@123"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

try:
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
except urllib.error.HTTPError as e:
    print("Status:", e.code, e.read().decode())

conn = sqlite3.connect("C:/Users/callm/nagriksetu/backend/data/nagriksetu.db")
conn.execute("DELETE FROM guardians WHERE guardian_id = ?", (dup_guardian2,))
conn.execute("DELETE FROM users WHERE user_id IN (?, ?)", (dup_user1, dup_user2))
conn.commit()
conn.close()
