import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for t in ["students", "enrollments", "guardians", "student_guardians"]:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"{t} columns:", cols)

# Search for any table or column related to attendance, test, marks, address
for t in tables:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()]
    att_cols = [c for c in cols if any(k in c.lower() for k in ["attend", "test", "mark", "exam", "grade", "score", "address"])]
    if att_cols or any(k in t.lower() for k in ["attend", "test", "mark", "exam", "grade", "score", "result"]):
        print(f"Matched {t}: {cols}")

conn.close()
