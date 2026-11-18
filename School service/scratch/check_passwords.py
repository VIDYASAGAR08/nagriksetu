from database import get_connection
from auth import verify_password

conn = get_connection()
admin = conn.execute("SELECT email, password_hash, role, school_id FROM users WHERE email='admin.sch001@example.com'").fetchone()
if admin:
    print("Admin found:", admin["email"], admin["role"], admin["school_id"])
    for test_pwd in ["Password@2026!", "Admin@SCH001", "Admin@NagrikSetu2026!", "Staff@NagrikSetu2026!", "Str0ngPass!2026"]:
        try:
            if verify_password(test_pwd, admin["password_hash"]):
                print(f"MATCH: {test_pwd}")
        except Exception as e:
            pass

for u in conn.execute("SELECT email, role, school_id, password_hash FROM users WHERE role IN ('school_admin', 'school_staff', 'admissions_officer') LIMIT 25").fetchall():
    for test_pwd in ["Password@2026!", "Admin@NagrikSetu2026!", "Staff@NagrikSetu2026!", "Str0ngPass!2026", "Central@NagrikSetu2026!"]:
        try:
            if verify_password(test_pwd, u["password_hash"]):
                print(f"Matched {u['email']} ({u['role']} {u['school_id']}): {test_pwd}")
                break
        except:
            pass

conn.close()
