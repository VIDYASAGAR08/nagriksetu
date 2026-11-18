import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for (t,) in tables:
    fks = c.execute(f"PRAGMA foreign_key_list({t})").fetchall()
    for fk in fks:
        if fk[2] == 'academic_programs':
            print(f"Table '{t}' references 'academic_programs':", fk)

conn.close()
