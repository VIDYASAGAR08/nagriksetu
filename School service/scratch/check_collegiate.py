import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("--- Check collegiate tables ---")
cur.execute("SELECT COUNT(*) FROM collegiate_enrollments")
print("collegiate_enrollments count:", cur.fetchone()[0])

cur.execute("SELECT school_id, COUNT(*) FROM students GROUP BY school_id")
for r in cur.fetchall():
    print(r)

conn.close()
