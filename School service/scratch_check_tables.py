import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
for t in ['user_institution_roles', 'invitation_tokens']:
    row = conn.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'").fetchone()
    if row:
        print(f"=== {t} ===")
        print(row[0])
conn.close()
