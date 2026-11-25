import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()
cur.execute("PRAGMA table_info(audit_logs)")
print("audit_logs:", [f"{c[1]} ({c[2]})" for c in cur.fetchall()])
conn.close()
