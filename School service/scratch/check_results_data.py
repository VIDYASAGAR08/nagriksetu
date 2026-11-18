import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("All tables:", tables)

results_count = c.execute("SELECT COUNT(*) FROM academic_results").fetchone()[0]
print("academic_results count:", results_count)
if results_count > 0:
    print("Sample academic_results:", c.execute("SELECT * FROM academic_results LIMIT 5").fetchall())

conn.close()
