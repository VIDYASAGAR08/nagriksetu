import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

tables = ['academic_programs', 'program_sections', 'institution_divisions', 'schools']
for t in tables:
    row = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()
    print(f"=== {t} ===")
    if row:
        print(row[0])
    print()

conn.close()
