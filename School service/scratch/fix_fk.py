import sqlite3
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.execute("DELETE FROM student_guardians WHERE rowid IN (5, 6)")
conn.commit()
print("FK violations now:", conn.execute("PRAGMA foreign_key_check").fetchall())
conn.close()
