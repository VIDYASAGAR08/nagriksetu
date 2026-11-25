import uuid

def handle_review_service_request(conn, inst_id, request_id, decision_type, comment_text, user):
    sr = conn.execute("""
        SELECT * FROM service_requests
        WHERE (request_id = ? OR tracking_number = ?)
          AND (assigned_institution_id = ? OR (assigned_institution_id IS NULL AND institution_id = ?))
    """, (request_id, request_id, inst_id, inst_id)).fetchone()
    
    if not sr:
        return None
    
    sr_dict = dict(sr)
    actual_req_id = sr_dict["request_id"]
    old_status = sr_dict["status"]
    admin_id = user["user_id"]
    admin_name = user.get("full_name") or "Institution Administrator"
    admin_role = user.get("role") or "school_admin"
    
    dt = decision_type.lower()
    if dt in ("approve", "approved", "correct", "corrected"):
        new_status = "CORRECTED"
        action_name = "RECORD_CORRECTED"
        field_name = (sr_dict.get("field_name") or "phone").lower().strip()
        new_val = str(sr_dict.get("requested_value") or "")
        old_val = str(sr_dict.get("current_value") or "")
        target_table = "guardians"
        record_id = sr_dict.get("permanent_student_id")
        
        # Apply data correction
        if sr_dict.get("target_module") == "guardians" or field_name in ("phone", "email", "address", "full_name"):
            target_table = "guardians"
            req_uid = sr_dict.get("requester_user_id")
            g_row = conn.execute("SELECT * FROM guardians WHERE user_id = ?", (req_uid,)).fetchone()
            if g_row:
                old_val = str(g_row[field_name] or "")
                conn.execute(f"UPDATE guardians SET {field_name} = ? WHERE guardian_id = ?", (new_val, g_row["guardian_id"]))
                record_id = g_row["guardian_id"]
            if field_name in ("phone", "email", "full_name") and req_uid:
                conn.execute(f"UPDATE users SET {field_name} = ? WHERE user_id = ?", (new_val, req_uid))
        elif field_name in ("date_of_birth", "student_name", "first_language", "gender"):
            target_table = "students"
            st_row = conn.execute("SELECT * FROM students WHERE permanent_student_id = ?", (sr_dict.get("permanent_student_id"),)).fetchone()
            if st_row:
                old_val = str(st_row[field_name] or "")
                conn.execute(f"UPDATE students SET {field_name} = ? WHERE permanent_student_id = ?", (new_val, sr_dict.get("permanent_student_id")))
        
        # Update service_requests
        conn.execute("""
            UPDATE service_requests
            SET status = 'CORRECTED',
                current_value = ?,
                resolved_at = DATETIME('now', 'localtime'),
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (new_val, actual_req_id))
        
        # Record into request_corrections
        corr_id = f"CORR-{uuid.uuid4().hex[:8].upper()}"
        conn.execute("""
            INSERT INTO request_corrections (
                correction_id, request_id, target_table, target_record_id, field_name,
                previous_value, corrected_value, correction_reason, administrator_id,
                administrator_name, administrator_role, verification_status, verified_by_user_id, verified_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'VERIFIED', ?, DATETIME('now', 'localtime'), DATETIME('now', 'localtime'))
        """, (corr_id, actual_req_id, target_table, record_id, field_name, old_val, new_val, comment_text, admin_id, admin_name, admin_role, admin_id))
        
    elif dt in ("reject", "rejected"):
        new_status = "REJECTED"
        action_name = "REQUEST_REJECTED"
        conn.execute("""
            UPDATE service_requests
            SET status = 'REJECTED',
                rejection_reason = ?,
                resolved_at = DATETIME('now', 'localtime'),
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (comment_text, actual_req_id))
    elif dt in ("clarify", "clarification_requested", "clarification_required"):
        new_status = "CLARIFICATION_REQUIRED"
        action_name = "CLARIFICATION_REQUESTED"
        conn.execute("""
            UPDATE service_requests
            SET status = 'CLARIFICATION_REQUIRED',
                clarification_prompt = ?,
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (comment_text, actual_req_id))
    else:
        new_status = "UNDER_REVIEW"
        action_name = "REQUEST_REVIEWED"
        conn.execute("UPDATE service_requests SET status = 'UNDER_REVIEW', updated_at = DATETIME('now', 'localtime') WHERE request_id = ?", (actual_req_id,))
        
    # Status history
    hist_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO request_status_history (
            history_id, request_id, from_status, to_status, action,
            actor_user_id, actor_name, actor_role, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'))
    """, (hist_id, actual_req_id, old_status, new_status, action_name, admin_id, admin_name, admin_role, comment_text or f"Status changed to {new_status}"))
    
    # Audit log
    audit_id = str(uuid.uuid4())
    details_json = f'{{"tracking_number": "{sr_dict.get("tracking_number")}", "action": "{action_name}", "decision": "{new_status}"}}'
    conn.execute("""
        INSERT INTO request_audit_logs (
            audit_id, request_id, actor_user_id, actor_role, action,
            entity_type, entity_id, school_id, details_json, created_at
        ) VALUES (?, ?, ?, ?, ?, 'service_requests', ?, ?, ?, DATETIME('now', 'localtime'))
    """, (audit_id, actual_req_id, admin_id, admin_role, action_name, actual_req_id, inst_id, details_json))
    
    return {
        "status": "success",
        "message": f"Request was successfully {new_status}.",
        "request_id": actual_req_id,
        "new_status": new_status
    }

print("Logic loaded successfully.")
