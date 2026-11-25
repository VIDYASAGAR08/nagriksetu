import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

for t in ["fees", "examinations", "academic_results", "student_attendance", "institution_announcements", "enrollments"]:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"{t}: {cols}")
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"  count: {count}")

conn.close()
