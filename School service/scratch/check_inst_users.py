import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("SELECT user_id, email, role, school_id, is_active, status FROM users WHERE school_id IN ('SCH001', 'SCH011', 'COL001', 'COL010')").fetchall()
for r in rows:
    print(dict(r))

# Also check user_institution_roles
uir = cur.execute("SELECT * FROM user_institution_roles WHERE institution_id IN ('SCH001', 'SCH011', 'COL001', 'COL010')").fetchall()
print("\nUser Institution Roles:")
for r in uir:
    print(dict(r))

conn.close()
