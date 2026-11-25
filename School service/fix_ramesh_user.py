import sqlite3
import uuid

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

# Restore staff-sch001-uid
c.execute("""
    UPDATE users
    SET role = 'school_staff', school_id = 'SCH001', email = 'staff.sch001@example.com', phone = '9845000001', full_name = 'Staff SCH001'
    WHERE user_id = 'staff-sch001-uid'
""")

# Create dedicated parent user for Ramesh Kumar
father_user_id = str(uuid.uuid4())
row = c.execute("SELECT password_hash FROM users WHERE role = 'parent' AND password_hash IS NOT NULL LIMIT 1").fetchone()
hash_val = row[0] if row else "$argon2id$v=19$m=65536,t=3,p=4$dummy"

c.execute("""
    INSERT INTO users (user_id, email, phone, password_hash, role, is_active, is_email_verified, full_name, status, created_at)
    VALUES (?, 'ramesh.kumar@example.com', '9845011001', ?, 'parent', 1, 1, 'Ramesh Kumar', 'active', CURRENT_TIMESTAMP)
""", (father_user_id, hash_val))

# Update guardian b320f710-7f5a-4456-b980-3c2429d5feb5 to point to father_user_id
c.execute("""
    UPDATE guardians
    SET user_id = ?
    WHERE guardian_id = 'b320f710-7f5a-4456-b980-3c2429d5feb5'
""", (father_user_id,))

conn.commit()
print("Restored staff-sch001-uid and created dedicated parent user for Ramesh Kumar:", father_user_id)
conn.close()
