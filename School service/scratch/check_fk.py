import sqlite3
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
print("FK violations:", conn.execute("PRAGMA foreign_key_check").fetchall())
conn.close()
