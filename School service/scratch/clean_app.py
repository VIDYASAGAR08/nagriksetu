import sqlite3
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.execute("DELETE FROM admission_detailed_submissions WHERE application_id='APP-2026-SCH001-6E341A'")
conn.execute("DELETE FROM admission_status_history WHERE application_id='APP-2026-SCH001-6E341A'")
conn.execute("DELETE FROM admission_applications WHERE application_id='APP-2026-SCH001-6E341A'")
conn.commit()
print("Applications count after cleanup:", conn.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0])
conn.close()
