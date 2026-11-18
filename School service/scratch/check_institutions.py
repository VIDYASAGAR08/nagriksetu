import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

inst_by_type = c.execute("SELECT school_type, category, COUNT(*), GROUP_CONCAT(school_id) FROM schools GROUP BY school_type, category").fetchall()
for row in inst_by_type:
    print(row)

print("\nAll institutions:")
for r in c.execute("SELECT school_id, school_name, school_type, category FROM schools ORDER BY school_id").fetchall():
    print(r)

conn.close()
