import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()

req_tables = ['service_requests', 'request_attachments', 'request_remarks', 'request_status_history', 'request_corrections', 'request_audit_logs', 'academic_result_audits', 'platform_audit_logs']
for t in req_tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [f"{c[1]} ({c[2]})" for c in cur.fetchall()]
    print(f"{t}: {cols}\n")

conn.close()
