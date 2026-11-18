import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cursor = conn.cursor()

tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("ALL TABLES IN DB:", tables)

adm_tables = [t for t in tables if 'admission' in t or 'notification' in t]
for t in adm_tables:
    print(f"\n--- SCHEMA FOR {t} ---")
    for col in cursor.execute(f"PRAGMA table_info({t})").fetchall():
        print(" ", col)
    cnt = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f" Count in {t}: {cnt}")

print("\n--- SAMPLE APPLICATION DATA IF ANY ---")
for t in adm_tables:
    rows = cursor.execute(f"SELECT * FROM {t} LIMIT 3").fetchall()
    print(f"Sample in {t}: {rows}")

print("\n--- CHECK EXISTING ADMISSION ROUTES IN BACKEND ---")
with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if any(kw in line for kw in ['/admissions', '/admission', 'Stage1ApplicationCreate', 'review_admission', '/school/admissions']):
            print(f"Line {i+1}: {line.strip()[:100]}")
