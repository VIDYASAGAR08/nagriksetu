import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()
cur.execute("SELECT user_id, institution_id, role, is_active FROM user_institution_roles LIMIT 5")
print("user_institution_roles:", cur.fetchall())

cur.execute("SELECT u.email, u.role, uir.institution_id FROM users u JOIN user_institution_roles uir ON uir.user_id = u.user_id WHERE uir.institution_id = 'SCH001'")
print("Admin for SCH001:", cur.fetchall())

conn.close()
