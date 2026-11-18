import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Check all tables related to admissions
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%admiss%' OR name LIKE '%doc%')").fetchall()]
print('Admission/Doc Tables:', tables)

# Print schema of detailed submissions / documents tables
for t in tables:
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"Schema of {t}: {cols}")

# 2. Check applications with stage2 in status or history
apps = cur.execute("""
    SELECT a.application_id, a.institution_id, a.applicant_name, a.status, a.updated_at
    FROM admission_applications a
    WHERE a.status LIKE '%stage2%' OR a.application_id IN (
        SELECT application_id FROM admission_status_history WHERE new_status LIKE '%stage2%'
    )
""").fetchall()
print('\nStage 2 Applications in admission_applications:')
for a in apps:
    print(dict(a))

# 3. Check status history for stage2_submitted
hist = cur.execute("""
    SELECT application_id, previous_status, new_status, action_note, created_at
    FROM admission_status_history
    WHERE new_status = 'stage2_submitted' OR previous_status = 'approved'
    ORDER BY created_at DESC
""").fetchall()
print('\nRecent History for approved / stage2_submitted:')
for h in hist:
    print(dict(h))
