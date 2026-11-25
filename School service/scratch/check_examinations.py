import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT * FROM examinations")
exams = cur.fetchall()
print(f"Total examinations in DB: {len(exams)}")
for e in exams[:10]:
    print(e)

conn.close()
