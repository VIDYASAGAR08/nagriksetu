import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()
for tbl in ['audit_logs', 'school_change_log', 'guardians', 'student_guardians']:
    sql = c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{tbl}'").fetchone()
    print(f"=== {tbl} ===")
    print(sql[0] if sql else "NOT FOUND")
