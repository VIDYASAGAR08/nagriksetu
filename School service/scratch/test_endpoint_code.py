# Test endpoint logic standalone
import sqlite3
import uuid
import datetime

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Test stats endpoint logic
inst_id = "SCH001"
tot_row = cur.execute("SELECT COUNT(*) AS total FROM students WHERE school_id = ?", (inst_id,)).fetchone()
act_row = cur.execute("SELECT COUNT(*) AS active FROM students WHERE school_id = ? AND (enrollment_status = 'active' OR enrollment_status IS NULL)", (inst_id,)).fetchone()
inact_row = cur.execute("SELECT COUNT(*) AS inactive FROM students WHERE school_id = ? AND enrollment_status NOT IN ('active') AND enrollment_status IS NOT NULL", (inst_id,)).fetchone()

std_rows = cur.execute("""
    SELECT standard, COUNT(*) AS count
    FROM students
    WHERE school_id = ?
    GROUP BY standard
    ORDER BY standard
""", (inst_id,)).fetchall()

rec_rows = cur.execute("""
    SELECT sra.audit_id, sra.student_id, sra.permanent_student_id, s.student_name,
           sra.field_modified, sra.previous_value, sra.updated_value, sra.reason,
           sra.source, sra.admin_name, sra.created_at
    FROM student_record_audits sra
    JOIN students s ON s.permanent_student_id = sra.permanent_student_id
    WHERE sra.institution_id = ?
    ORDER BY sra.created_at DESC
    LIMIT 10
""", (inst_id,)).fetchall()

pend_rows = cur.execute("""
    SELECT request_id, tracking_number, title, category, priority,
           affected_person_name, affected_student_id, permanent_student_id,
           field_name, current_value, requested_value, status, submitted_at
    FROM service_requests
    WHERE (assigned_institution_id = ? OR institution_id = ?)
      AND status IN ('PENDING', 'SUBMITTED', 'UNDER_INVESTIGATION', 'CLARIFICATION_PROVIDED')
    ORDER BY submitted_at DESC
    LIMIT 10
""", (inst_id, inst_id)).fetchall()

stats = {
    "total_students": tot_row["total"],
    "active_students": act_row["active"],
    "inactive_students": inact_row["inactive"],
    "by_standard": [{"standard": r["standard"], "label": f"Standard {r['standard']}" if r["standard"] and r["standard"] <= 10 else f"{r['standard']}th", "count": r["count"]} for r in std_rows],
    "recently_updated": [dict(r) for r in rec_rows],
    "pending_correction_requests_count": len(pend_rows),
    "pending_correction_requests": [dict(r) for r in pend_rows]
}
print("Stats output successfully generated:")
print("  Total:", stats["total_students"])
print("  Active:", stats["active_students"])
print("  Standards count:", len(stats["by_standard"]))
print("  Pending requests:", stats["pending_correction_requests_count"])

conn.close()
