from database import get_connection
from auth import verify_password, hash_password

conn = get_connection()
u = conn.execute("SELECT user_id, email, phone, role, password_hash FROM users WHERE role = 'platform_admin'").fetchall()
for r in u:
    print("Platform admin:", dict(r))
