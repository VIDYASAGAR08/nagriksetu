import sqlite3
import json

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row

cursor = conn.cursor()
tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("All tables in SQLite:")
print(tables)

request_related = [t for t in tables if any(k in t.lower() for k in ["request", "complaint", "correct", "ticket", "notif", "audit"])]
print("\nRequest / Correction / Notification related tables:")
print(request_related)

for t in request_related:
    print(f"\n--- Schema for table: {t} ---")
    cols = cursor.execute(f"PRAGMA table_info({t})").fetchall()
    for c in cols:
        print(f"  {c['name']} ({c['type']})")
    count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  Row count: {count}")
    sample = cursor.execute(f"SELECT * FROM {t} LIMIT 2").fetchall()
    for s in sample:
        print(f"  Sample row: {dict(s)}")

conn.close()
