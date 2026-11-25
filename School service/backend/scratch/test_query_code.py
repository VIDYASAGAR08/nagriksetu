import sqlite3

db_path = r"C:\Users\callm\Nagriksetu School Service\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

def get_institution_parent_requests_test(inst_id, status="all"):
    sr_clauses = ["(sr.assigned_institution_id = ? OR (sr.assigned_institution_id IS NULL AND sr.institution_id = ?))"]
    sr_params = [inst_id, inst_id]

    ur_clauses = ["s.school_id = ?"]
    ur_params = [inst_id]

    if status and status != "all":
        st = status.strip().lower()
        if st in ("pending", "submitted", "under_review"):
            sr_clauses.append("sr.status IN ('SUBMITTED', 'UNDER_REVIEW', 'pending')")
            ur_clauses.append("ur.status IN ('pending', 'submitted')")
        elif st in ("approved", "accepted", "corrected", "verified"):
            sr_clauses.append("sr.status IN ('ACCEPTED', 'CORRECTED', 'VERIFIED', 'approved')")
            ur_clauses.append("ur.status IN ('approved', 'accepted')")
        elif st in ("rejected", "cancelled"):
            sr_clauses.append("sr.status IN ('REJECTED', 'rejected')")
            ur_clauses.append("ur.status IN ('rejected', 'cancelled')")
        elif st in ("clarification_requested", "clarification_required"):
            sr_clauses.append("sr.status IN ('CLARIFICATION_REQUIRED', 'RESUBMITTED', 'clarification_requested')")
            ur_clauses.append("ur.status IN ('clarification_requested', 'clarification_required')")
        else:
            sr_clauses.append("(LOWER(sr.status) = ? OR UPPER(sr.status) = ?)")
            sr_params.extend([st, st.upper()])
            ur_clauses.append("LOWER(ur.status) = ?")
            ur_params.append(st)

    sr_sql = " AND ".join(sr_clauses)
    ur_sql = " AND ".join(ur_clauses)

    sr_rows = conn.execute(f"""
        SELECT sr.request_id, sr.tracking_number, sr.permanent_student_id,
               sr.affected_student_id AS student_id,
               COALESCE(sr.affected_person_name, s.student_name, 'Enrolled Student') AS student_name,
               COALESCE(sr.requester_name, g.full_name, 'Parent / Guardian') AS parent_name,
               COALESCE(sr.requester_phone, g.phone) AS parent_phone,
               COALESCE(sr.requester_email, g.email) AS parent_email,
               COALESCE(sr.field_name, sr.category) AS field_name,
               sr.current_value AS old_value,
               sr.current_value,
               sr.requested_value AS proposed_value,
               sr.requested_value,
               sr.description AS reason,
               sr.status,
               sr.submitted_at,
               sr.submitted_at AS created_at,
               sr.resolved_at AS reviewed_at,
               COALESCE(sr.rejection_reason, sr.clarification_prompt) AS review_comment,
               sr.category,
               sr.priority,
               sr.target_module,
               sr.target_record_id,
               'service_requests' AS source_table
        FROM service_requests sr
        LEFT JOIN students s ON s.permanent_student_id = sr.permanent_student_id
        LEFT JOIN student_guardians sg ON sg.permanent_student_id = sr.permanent_student_id AND sg.is_verified = 1
        LEFT JOIN guardians g ON g.guardian_id = sg.guardian_id
        WHERE {sr_sql}
        ORDER BY sr.submitted_at DESC
    """, sr_params).fetchall()

    ur_rows = conn.execute(f"""
        SELECT ur.request_id, ur.request_id AS tracking_number, ur.permanent_student_id,
               s.student_id, s.student_name,
               g.full_name AS parent_name, g.phone AS parent_phone, g.email AS parent_email,
               ur.field_name, ur.old_value, ur.proposed_value,
               ur.proposed_value AS requested_value, ur.old_value AS current_value,
               ur.reason, ur.status, ur.submitted_at, ur.submitted_at AS created_at,
               ur.reviewed_at, ur.review_comment,
               ur.request_type AS category, 'medium' AS priority, 'students' AS target_module,
               ur.permanent_student_id AS target_record_id,
               'update_requests' AS source_table
        FROM update_requests ur
        JOIN students s ON s.permanent_student_id = ur.permanent_student_id
        JOIN guardians g ON g.guardian_id = ur.guardian_id
        WHERE {ur_sql}
        ORDER BY ur.submitted_at DESC
    """, ur_params).fetchall()

    # Merge and deduplicate by request_id
    seen = set()
    combined = []
    for r in list(sr_rows) + list(ur_rows):
        d = dict(r)
        if d['request_id'] not in seen:
            seen.add(d['request_id'])
            combined.append(d)

    return combined

res = get_institution_parent_requests_test('SCH017')
print(f"Results for SCH017 (count={len(res)}):")
for r in res:
    print(r)
