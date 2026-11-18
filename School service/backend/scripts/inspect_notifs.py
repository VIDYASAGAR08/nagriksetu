import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()
tables = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Total tables:", len(tables))

notif_tables = [t for t in tables if any(k in t.lower() for k in ['notif', 'pref', 'comm', 'msg', 'alert', 'announc'])]
print("Matching tables:", notif_tables)

for t in notif_tables:
    cols = c.execute(f"PRAGMA table_info({t})").fetchall()
    print(f"\nTable {t}:")
    for col in cols:
        print(f"  {col[1]} ({col[2]})")
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"  Row count: {count}")
    if count > 0:
        sample = c.execute(f"SELECT * FROM {t} LIMIT 2").fetchall()
        print(f"  Sample row: {sample[0]}")

conn.close()
