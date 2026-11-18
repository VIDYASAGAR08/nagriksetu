import sqlite3
import json

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

app_id = 'APP-2026-SCH019-6ED0FE'
school_id = 'SCH019'

row = cur.execute("""
    SELECT a.*, s.school_name, p.program_name
    FROM admission_applications a
    JOIN schools s ON s.school_id = a.institution_id
    LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
    WHERE a.application_id = ? AND a.institution_id = ?
""", (app_id, school_id)).fetchone()

data = dict(row)
hist = cur.execute("SELECT * FROM admission_status_history WHERE application_id = ? ORDER BY created_at ASC", (app_id,)).fetchall()
data["status_history"] = [dict(h) for h in hist]

detailed_row = cur.execute("""
    SELECT submission_id, application_id, date_of_birth, gender, blood_group,
           previous_institution_name, previous_institution_location,
           previous_standard_or_degree, previous_board, previous_marks_percentage,
           emergency_contact_name, emergency_contact_phone, custom_fields_json,
           status, submitted_at
    FROM admission_detailed_submissions
    WHERE application_id = ?
    ORDER BY submitted_at DESC
    LIMIT 1
""", (app_id,)).fetchone()

if detailed_row:
    s2 = dict(detailed_row)
    s2["custom_fields"] = json.loads(s2["custom_fields_json"]) if s2.get("custom_fields_json") else {}
    data["stage2_details"] = s2
    data["stage2_submitted"] = True

doc_rows = cur.execute("""
    SELECT document_id, application_id, document_type, file_name, file_size_bytes,
           mime_type, verification_status, uploaded_at, verified_by_user_id,
           verified_at, verification_notes
    FROM admission_documents
    WHERE application_id = ?
    ORDER BY uploaded_at ASC
""", (app_id,)).fetchall()

data["documents"] = [dict(dr) for dr in doc_rows]

print("Keys in enriched data:", list(data.keys()))
print("Stage 2 Details:", data["stage2_details"])
print("Document count:", len(data["documents"]))
for d in data["documents"]:
    print("  -", d["document_type"], "|", d["file_name"], "| status:", d["verification_status"])
