import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(schools)")
cols = cur.fetchall()
print("Columns in schools:")
for c in cols:
    print(f"  {c[1]}: {c[2]}")

cur.execute("SELECT school_id, school_name, capacity FROM schools LIMIT 10")
print("Sample capacity values:", cur.fetchall())

conn.close()
