import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
found = False
for t in tables:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
    for col in cols:
        try:
            cnt = c.execute(f"SELECT COUNT(*) FROM {t} WHERE CAST({col} AS TEXT) LIKE '%Raju%'").fetchone()[0]
            if cnt > 0:
                found = True
                print(f"Found {cnt} rows in table {t}, column {col} matching 'Raju':")
                rows = c.execute(f"SELECT * FROM {t} WHERE CAST({col} AS TEXT) LIKE '%Raju%' LIMIT 5").fetchall()
                for r in rows:
                    print("  ", r)
        except Exception:
            pass

if not found:
    print("No occurrences of 'Raju' found in any table in the database.")

conn.close()
