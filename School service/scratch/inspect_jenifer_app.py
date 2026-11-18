import sqlite3
import json

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

app_id = 'APP-2026-SCH019-6ED0FE'

print("=== ADMISSION APPLICATION ===")
app = cur.execute("SELECT * FROM admission_applications WHERE application_id = ?", (app_id,)).fetchone()
if app:
    print(dict(app))

print("\n=== DETAILED SUBMISSION ===")
det = cur.execute("SELECT * FROM admission_detailed_submissions WHERE application_id = ?", (app_id,)).fetchall()
for d in det:
    print(dict(d))

print("\n=== ADMISSION DOCUMENTS ===")
docs = cur.execute("SELECT * FROM admission_documents WHERE application_id = ?", (app_id,)).fetchall()
for doc in docs:
    print(dict(doc))

print("\n=== STATUS HISTORY ===")
hist = cur.execute("SELECT * FROM admission_status_history WHERE application_id = ? ORDER BY created_at ASC", (app_id,)).fetchall()
for h in hist:
    print(dict(h))
