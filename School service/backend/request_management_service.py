import uuid
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field

from database import get_connection
from auth import get_current_user

router = APIRouter(prefix="", tags=["Service Requests & Correction Management"])

SUPPORTED_CATEGORIES = [
    "Attendance Correction",
    "Student Personal Information Correction",
    "Parent / Guardian Information Correction",
    "Mobile Number Update",
    "Email Address Update",
    "Residential Address Update",
    "Date of Birth Correction",
    "Student Name Correction",
    "Examination Marks Correction",
    "Examination Result Correction",
    "Academic Record Correction",
    "Fee Record Clarification",
    "Admission Information Correction",
    "Parent-Student Linking Issue",
    "Institution Complaint",
    "Staff / Faculty Complaint",
    "General Clarification",
    "Other Requests"
]

INSTITUTION_CATEGORIES = {
    "Attendance Correction",
    "Student Personal Information Correction",
    "Parent / Guardian Information Correction",
    "Mobile Number Update",
    "Email Address Update",
    "Residential Address Update",
    "Date of Birth Correction",
    "Student Name Correction",
    "Examination Marks Correction",
    "Examination Result Correction",
    "Academic Record Correction",
    "Fee Record Clarification",
    "Admission Information Correction",
    "Parent-Student Linking Issue",
    "Institution Complaint",
    "Staff / Faculty Complaint"
}


# --- Request & Payload Schemas ---

class CreateServiceRequestPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    category: str
    description: str = Field(..., min_length=5, max_length=2000)
    priority: Optional[str] = "medium"  # low, medium, high, urgent
    affected_person_type: Optional[str] = "self"  # self, linked_child, staff, other
    affected_student_id: Optional[str] = None
    institution_id: Optional[str] = None
    target_module: Optional[str] = None
    target_record_id: Optional[str] = None
    field_name: Optional[str] = None
    current_value: Optional[str] = None
    requested_value: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    supporting_document_url: Optional[str] = None
    supporting_document_name: Optional[str] = None


class AddRemarkPayload(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    visibility: str = "requester_visible"  # requester_visible or internal_only


class ClarificationPromptPayload(BaseModel):
    clarification_prompt: str = Field(..., min_length=5, max_length=2000)
    remarks: Optional[str] = None


class ClarificationResponsePayload(BaseModel):
    response_message: str = Field(..., min_length=2, max_length=2000)
    additional_document_url: Optional[str] = None
    additional_document_name: Optional[str] = None


class RejectRequestPayload(BaseModel):
    rejection_reason: str = Field(..., min_length=5, max_length=1000)
    remarks: Optional[str] = None


class AcceptRequestPayload(BaseModel):
    remarks: Optional[str] = None
    requires_correction: bool = False


class ExecuteCorrectionPayload(BaseModel):
    target_module: str  # attendance, student_profile, personal_info, parent_info, examination_marks
    target_record_id: str  # date or id for attendance, student_id/PSID, result_id, user_id
    field_name: str
    proposed_new_value: str
    confirmation_remarks: str = Field(..., min_length=3, max_length=1000)
    verification_evidence_ref: Optional[str] = None


class ForwardRequestPayload(BaseModel):
    target_institution_id: str
    forward_remarks: Optional[str] = None


# --- Helper Functions ---

def generate_request_id() -> str:
    short_uuid = uuid.uuid4().hex[:8].upper()
    return f"REQ-2026-{short_uuid}"

def generate_tracking_number() -> str:
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"TRK-{short_uuid}"

def dispatch_notification(
    conn: sqlite3.Connection,
    recipient_user_id: Optional[str] = None,
    recipient_role: Optional[str] = None,
    institution_id: Optional[str] = None,
    title: str = "",
    message: str = "",
    action_url: str = "",
    category: str = "service_request",
    priority: str = "normal"
):
    notif_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO portal_notifications (
            notification_id, recipient_user_id, recipient_role, institution_id,
            title, message, action_url, is_read, category, priority, channel, delivery_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 'in_app', 'delivered', DATETIME('now', 'localtime'))
    """, (notif_id, recipient_user_id, recipient_role, institution_id, title, message, action_url, category, priority))

def add_status_history(
    conn: sqlite3.Connection,
    request_id: str,
    from_status: Optional[str],
    to_status: str,
    action: str,
    actor_user_id: str,
    actor_name: Optional[str],
    actor_role: Optional[str],
    notes: Optional[str] = None
):
    hist_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO request_status_history (
            history_id, request_id, from_status, to_status, action,
            actor_user_id, actor_name, actor_role, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'))
    """, (hist_id, request_id, from_status, to_status, action, actor_user_id, actor_name, actor_role, notes))

def add_audit_log(
    conn: sqlite3.Connection,
    request_id: str,
    actor_user_id: str,
    actor_role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    school_id: Optional[str],
    details: Dict[str, Any]
):
    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO request_audit_logs (
            audit_id, request_id, actor_user_id, actor_role, action,
            entity_type, entity_id, school_id, details_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'))
    """, (audit_id, request_id, actor_user_id, actor_role, action, entity_type, entity_id, school_id, json.dumps(details)))


# ==============================================================================
# 1. REQUESTER APIS (Students, Parents, Citizens, Staff)
# ==============================================================================

@router.post("/requests/raise", status_code=201)
def raise_service_request(
    payload: CreateServiceRequestPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Authenticated user raises a request, clarification, complaint or record correction.
    Validates authority over the affected person (e.g. verified linked child for parent).
    Automatically routes to responsible Institution Administrator or Platform Administrator.
    """
    conn = get_connection()
    try:
        user_id = current_user["user_id"]
        role = current_user["role"]
        user_name = current_user.get("full_name") or current_user.get("student_name") or "User"
        user_email = current_user.get("email")
        user_phone = current_user.get("phone")

        if payload.category not in SUPPORTED_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request category '{payload.category}'. Must be one of the 18 approved categories."
            )

        # Authority and Affected Person Validation
        target_psid = None
        target_student_id = None
        target_student_name = None
        resolved_inst_id = (payload.institution_id or "").strip() or None

        if payload.affected_student_id:
            st_query = (payload.affected_student_id or "").strip()
            st_row = conn.execute("""
                SELECT student_id, permanent_student_id, student_name, school_id
                FROM students
                WHERE student_id = ? OR permanent_student_id = ?
            """, (st_query, st_query)).fetchone()

            if not st_row:
                raise HTTPException(status_code=404, detail=f"Affected Student ID '{st_query}' not found in database.")

            target_student_id = st_row["student_id"]
            target_psid = st_row["permanent_student_id"]
            target_student_name = st_row["student_name"]
            resolved_inst_id = st_row["school_id"]

            # Permission check: Parent must have verified relationship
            if role == "parent":
                g_row = conn.execute("SELECT guardian_id FROM guardians WHERE user_id = ?", (user_id,)).fetchone()
                if not g_row:
                    raise HTTPException(status_code=403, detail="No guardian profile associated with this parent account.")
                
                link_row = conn.execute("""
                    SELECT is_verified, can_request_updates FROM student_guardians
                    WHERE guardian_id = ? AND permanent_student_id = ?
                """, (g_row["guardian_id"], target_psid)).fetchone()

                if not link_row or link_row["is_verified"] != 1:
                    raise HTTPException(
                        status_code=403,
                        detail="Access Denied: You may only raise record correction requests for verified linked children."
                    )
            elif role == "student":
                # Student must only raise for self
                if current_user.get("student_id") != target_student_id and current_user.get("permanent_student_id") != target_psid:
                    raise HTTPException(status_code=403, detail="Students can only submit requests regarding their own records.")
        elif role == "student":
            target_student_id = current_user.get("student_id")
            target_psid = current_user.get("permanent_student_id")
            target_student_name = current_user.get("student_name") or user_name
            resolved_inst_id = current_user.get("school_id")

        elif role == "parent" and not resolved_inst_id:
            # If parent raised request for self (e.g. mobile/email update) without specifying institution,
            # resolve to their verified linked child's institution.
            g_row = conn.execute("SELECT guardian_id FROM guardians WHERE user_id = ?", (user_id,)).fetchone()
            if g_row:
                link_inst = conn.execute("""
                    SELECT s.school_id, s.permanent_student_id, s.student_name, s.student_id
                    FROM student_guardians sg
                    JOIN students s ON s.permanent_student_id = sg.permanent_student_id
                    WHERE sg.guardian_id = ? AND sg.is_verified = 1
                    ORDER BY sg.created_at DESC
                    LIMIT 1
                """, (g_row["guardian_id"],)).fetchone()
                if link_inst:
                    resolved_inst_id = link_inst["school_id"]
                    if not target_psid:
                        target_psid = link_inst["permanent_student_id"]
                        target_student_id = link_inst["student_id"]
                        target_student_name = link_inst["student_name"]

        # Routing tier logic
        routing_tier = "institution"
        if payload.category in INSTITUTION_CATEGORIES:
            routing_tier = "institution"
            if not resolved_inst_id:
                resolved_inst_id = current_user.get("school_id")
        else:
            # Platform or institution
            if resolved_inst_id:
                routing_tier = "institution"
            else:
                routing_tier = "platform"

        req_id = generate_request_id()
        trk_no = generate_tracking_number()

        conn.execute("""
            INSERT INTO service_requests (
                request_id, tracking_number, title, category, description, priority,
                requester_user_id, requester_role, requester_name, requester_email, requester_phone,
                affected_person_type, affected_student_id, permanent_student_id, affected_person_name,
                institution_id, target_module, target_record_id, field_name, current_value, requested_value,
                status, routing_tier, assigned_institution_id, submitted_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                'SUBMITTED', ?, ?, DATETIME('now', 'localtime'), DATETIME('now', 'localtime')
            )
        """, (
            req_id, trk_no, payload.title.strip(), payload.category, payload.description.strip(), payload.priority or "medium",
            user_id, role, user_name, payload.contact_email or user_email, payload.contact_phone or user_phone,
            payload.affected_person_type or "self", target_student_id, target_psid, target_student_name,
            resolved_inst_id, payload.target_module, payload.target_record_id, payload.field_name,
            payload.current_value, payload.requested_value,
            routing_tier, resolved_inst_id
        ))

        # Attachments
        if payload.supporting_document_url:
            att_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO request_attachments (
                    attachment_id, request_id, uploaded_by_user_id, file_name, file_url_or_path, purpose, created_at
                ) VALUES (?, ?, ?, ?, ?, 'supporting_document', DATETIME('now', 'localtime'))
            """, (att_id, req_id, user_id, payload.supporting_document_name or "Supporting_Document.pdf", payload.supporting_document_url))

        # Initial Status History
        add_status_history(
            conn=conn,
            request_id=req_id,
            from_status=None,
            to_status="SUBMITTED",
            action="REQUEST_SUBMITTED",
            actor_user_id=user_id,
            actor_name=user_name,
            actor_role=role,
            notes=f"Request submitted under category '{payload.category}'. Priority: {payload.priority}."
        )

        # Audit Log
        add_audit_log(
            conn=conn,
            request_id=req_id,
            actor_user_id=user_id,
            actor_role=role,
            action="SERVICE_REQUEST_SUBMITTED",
            entity_type="service_requests",
            entity_id=req_id,
            school_id=resolved_inst_id,
            details={
                "tracking_number": trk_no,
                "category": payload.category,
                "title": payload.title,
                "routing_tier": routing_tier,
                "assigned_institution_id": resolved_inst_id
            }
        )

        # In-App Notifications
        # 1. To Requester
        dispatch_notification(
            conn=conn,
            recipient_user_id=user_id,
            institution_id=resolved_inst_id,
            title="Request Submitted Successfully",
            message=f"Your request '{payload.title}' ({req_id}) has been recorded and submitted for institutional review.",
            action_url=f"/requests/{req_id}",
            category="service_request",
            priority="normal"
        )

        # 2. To Responsible Administrator
        if routing_tier == "institution" and resolved_inst_id:
            dispatch_notification(
                conn=conn,
                recipient_role="school_admin",
                institution_id=resolved_inst_id,
                title=f"New Request Received: {payload.category}",
                message=f"A new {payload.priority} priority request was submitted by {user_name} ({role}) regarding {target_student_name or 'institution matters'}.",
                action_url=f"/institution/{resolved_inst_id}/requests?request_id={req_id}",
                category="service_request",
                priority="high" if payload.priority in ("high", "urgent") else "normal"
            )
        else:
            dispatch_notification(
                conn=conn,
                recipient_role="platform_admin",
                title=f"Platform Request: {payload.category}",
                message=f"A new platform request ({req_id}) was submitted by {user_name}.",
                action_url=f"/admin/requests?request_id={req_id}",
                category="service_request",
                priority="normal"
            )

        conn.commit()

        return {
            "status": "success",
            "message": "Your request has been submitted successfully.",
            "request_id": req_id,
            "tracking_number": trk_no,
            "review_status": "SUBMITTED",
            "routing_tier": routing_tier,
            "assigned_institution_id": resolved_inst_id,
            "submitted_at": datetime.now().isoformat()
        }
    finally:
        conn.close()


@router.get("/requests/my-requests")
def list_my_service_requests(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Returns all requests submitted by the authenticated user with status lifecycle and summaries.
    """
    conn = get_connection()
    try:
        user_id = current_user["user_id"]
        where_clauses = ["sr.requester_user_id = ?"]
        params = [user_id]

        if category:
            where_clauses.append("sr.category = ?")
            params.append(category)

        if status_filter:
            where_clauses.append("sr.status = ?")
            params.append(status_filter.upper())

        where_sql = " AND ".join(where_clauses)
        rows = conn.execute(f"""
            SELECT sr.*, s.school_name AS institution_name
            FROM service_requests sr
            LEFT JOIN schools s ON s.school_id = sr.assigned_institution_id
            WHERE {where_sql}
            ORDER BY sr.submitted_at DESC
        """, tuple(params)).fetchall()

        results = []
        for r in rows:
            d = dict(r)
            req_id = d["request_id"]
            
            # Check for corrections and remarks count
            corr_count = conn.execute("SELECT count(*) FROM request_corrections WHERE request_id = ?", (req_id,)).fetchone()[0]
            rem_count = conn.execute("SELECT count(*) FROM request_remarks WHERE request_id = ? AND visibility = 'requester_visible'", (req_id,)).fetchone()[0]
            
            d["has_corrections"] = corr_count > 0
            d["requester_remarks_count"] = rem_count
            d["has_rejection_reason"] = bool(d.get("rejection_reason"))
            d["has_clarification_prompt"] = bool(d.get("clarification_prompt"))
            results.append(d)

        return results
    finally:
        conn.close()


@router.get("/requests/{request_id}")
def get_service_request_details(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Detailed request view including chronological timeline, attachments, requester-visible remarks,
    and verified correction details. Internal admin remarks are strictly hidden from requesters.
    """
    conn = get_connection()
    try:
        user_id = current_user["user_id"]
        user_role = current_user["role"]
        user_school_id = current_user.get("school_id")

        row = conn.execute("""
            SELECT sr.*, s.school_name AS institution_name, s.school_type
            FROM service_requests sr
            LEFT JOIN schools s ON s.school_id = sr.assigned_institution_id
            WHERE sr.request_id = ? OR sr.tracking_number = ?
        """, (request_id, request_id)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Request '{request_id}' not found.")

        req_dict = dict(row)
        req_id = req_dict["request_id"]
        req_owner_id = req_dict["requester_user_id"]
        assigned_inst = req_dict.get("assigned_institution_id")

        # Security check:
        # Requesters can only view their own requests.
        # Institution Admin can view if assigned_institution_id matches.
        # Platform Admin can view all.
        is_owner = (user_id == req_owner_id)
        is_inst_admin = (user_role in ("school_admin", "academic_admin", "institution_admin", "school_staff") and user_school_id == assigned_inst)
        is_plat_admin = (user_role == "platform_admin")

        if not (is_owner or is_inst_admin or is_plat_admin):
            raise HTTPException(status_code=403, detail="Access Denied: You do not have permission to view this request.")

        # Remarks: Requester sees only requester_visible; Admin sees all
        if is_owner and not (is_inst_admin or is_plat_admin):
            rem_rows = conn.execute("""
                SELECT remark_id, author_name, author_role, message, created_at, visibility
                FROM request_remarks
                WHERE request_id = ? AND visibility = 'requester_visible'
                ORDER BY created_at ASC
            """, (req_id,)).fetchall()
        else:
            rem_rows = conn.execute("""
                SELECT remark_id, author_name, author_role, message, created_at, visibility
                FROM request_remarks
                WHERE request_id = ?
                ORDER BY created_at ASC
            """, (req_id,)).fetchall()

        # Status History Timeline
        hist_rows = conn.execute("""
            SELECT history_id, from_status, to_status, action, actor_name, actor_role, notes, created_at
            FROM request_status_history
            WHERE request_id = ?
            ORDER BY created_at ASC
        """, (req_id,)).fetchall()

        # Attachments
        att_rows = conn.execute("""
            SELECT attachment_id, file_name, file_url_or_path, purpose, created_at
            FROM request_attachments
            WHERE request_id = ?
            ORDER BY created_at ASC
        """, (req_id,)).fetchall()

        # Corrections
        corr_rows = conn.execute("""
            SELECT correction_id, target_table, target_record_id, field_name, previous_value,
                   corrected_value, correction_reason, administrator_name, administrator_role,
                   verification_status, verified_at, created_at
            FROM request_corrections
            WHERE request_id = ?
            ORDER BY created_at DESC
        """, (req_id,)).fetchall()

        remarks_list = [dict(r) for r in rem_rows]
        timeline_list = [dict(h) for h in hist_rows]
        attachments_list = [dict(a) for a in att_rows]
        corrections_list = [dict(c) for c in corr_rows]

        req_dict["remarks"] = remarks_list
        req_dict["timeline"] = timeline_list
        req_dict["status_history"] = timeline_list
        req_dict["attachments"] = attachments_list
        req_dict["corrections"] = corrections_list

        result = dict(req_dict)
        result["request"] = dict(req_dict)
        result["remarks"] = remarks_list
        result["timeline"] = timeline_list
        result["status_history"] = timeline_list
        result["attachments"] = attachments_list
        result["corrections"] = corrections_list

        return result
    finally:
        conn.close()


@router.post("/requests/{request_id}/respond-clarification")
def respond_to_clarification(
    request_id: str,
    payload: ClarificationResponsePayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Requester responds to a clarification prompt by providing additional details or supporting proof.
    Transitions status to UNDER_REVIEW (or RESUBMITTED) and alerts the reviewing administrator.
    """
    conn = get_connection()
    try:
        user_id = current_user["user_id"]
        user_name = current_user.get("full_name") or current_user.get("student_name") or "Requester"
        user_role = current_user["role"]

        row = conn.execute("""
            SELECT request_id, requester_user_id, status, assigned_institution_id, title
            FROM service_requests
            WHERE request_id = ?
        """, (request_id,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Request not found.")

        if row["requester_user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Only the original requester can respond to clarification.")

        if row["status"] != "CLARIFICATION_REQUIRED":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot respond to clarification when request status is '{row['status']}'. Must be CLARIFICATION_REQUIRED."
            )

        resp_text = payload.response_message.strip()

        # Add attachment if provided
        if payload.additional_document_url:
            att_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO request_attachments (
                    attachment_id, request_id, uploaded_by_user_id, file_name, file_url_or_path, purpose, created_at
                ) VALUES (?, ?, ?, ?, ?, 'clarification_response', DATETIME('now', 'localtime'))
            """, (att_id, request_id, user_id, payload.additional_document_name or "Clarification_Document.pdf", payload.additional_document_url))

        # Add remark
        rem_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO request_remarks (
                remark_id, request_id, author_user_id, author_name, author_role, message, visibility, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'requester_visible', DATETIME('now', 'localtime'))
        """, (rem_id, request_id, user_id, user_name, user_role, f"Requester Clarification Response: {resp_text}"))

        # Transition status to UNDER_REVIEW
        conn.execute("""
            UPDATE service_requests
            SET status = 'UNDER_REVIEW',
                requester_response = ?,
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (resp_text, request_id))

        # Status History
        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status="CLARIFICATION_REQUIRED",
            to_status="UNDER_REVIEW",
            action="CLARIFICATION_PROVIDED",
            actor_user_id=user_id,
            actor_name=user_name,
            actor_role=user_role,
            notes=resp_text
        )

        # Notify assigned admin
        inst_id = row["assigned_institution_id"]
        if inst_id:
            dispatch_notification(
                conn=conn,
                recipient_role="school_admin",
                institution_id=inst_id,
                title=f"Clarification Response Received ({request_id})",
                message=f"Requester {user_name} provided clarification for '{row['title']}'. Request is now under review.",
                action_url=f"/institution/{inst_id}/requests?request_id={request_id}",
                category="service_request",
                priority="normal"
            )

        conn.commit()
        return {
            "status": "success",
            "request_status": "UNDER_REVIEW",
            "new_status": "UNDER_REVIEW",
            "message": "Clarification response submitted successfully. Status updated to UNDER_REVIEW."
        }
    finally:
        conn.close()


# ==============================================================================
# 2. INSTITUTION ADMINISTRATOR APIS
# ==============================================================================

@router.get("/institution/{institution_id}/requests")
def list_institution_service_requests(
    institution_id: str,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Displays service requests belonging strictly to the administrator's assigned institution.
    Provides filterable lifecycle statuses and summary counts.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        where_clauses = ["sr.assigned_institution_id = ?"]
        params = [institution_id]

        if status_filter and status_filter.upper() != "ALL":
            where_clauses.append("sr.status = ?")
            params.append(status_filter.upper())

        if category and category.lower() != "all":
            where_clauses.append("sr.category = ?")
            params.append(category)

        if search:
            search_pattern = f"%{search.strip()}%"
            where_clauses.append("(sr.request_id LIKE ? OR sr.tracking_number LIKE ? OR sr.title LIKE ? OR sr.affected_student_id LIKE ? OR sr.affected_person_name LIKE ?)")
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        where_sql = " AND ".join(where_clauses)
        rows = conn.execute(f"""
            SELECT sr.*, s.school_name AS institution_name
            FROM service_requests sr
            LEFT JOIN schools s ON s.school_id = sr.assigned_institution_id
            WHERE {where_sql}
            ORDER BY 
                CASE sr.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END,
                sr.submitted_at DESC
        """, tuple(params)).fetchall()

        # Compute summary metrics by status for dashboard tabs
        counts_rows = conn.execute("""
            SELECT status, count(*) AS count
            FROM service_requests
            WHERE assigned_institution_id = ?
            GROUP BY status
        """, (institution_id,)).fetchall()

        status_counts = {r["status"]: r["count"] for r in counts_rows}
        status_counts["ALL"] = sum(status_counts.values())

        summary = {
            "total": status_counts.get("ALL", 0),
            "submitted": status_counts.get("SUBMITTED", 0),
            "under_review": status_counts.get("UNDER_REVIEW", 0),
            "clarification_required": status_counts.get("CLARIFICATION_REQUIRED", 0),
            "corrected": status_counts.get("CORRECTED", 0),
            "rejected": status_counts.get("REJECTED", 0)
        }

        return {
            "institution_id": institution_id,
            "status_counts": status_counts,
            "summary": summary,
            "total_count": len(rows),
            "requests": [dict(r) for r in rows]
        }
    finally:
        conn.close()


@router.post("/institution/{institution_id}/requests/{request_id}/accept")
def accept_service_request(
    institution_id: str,
    request_id: str,
    payload: AcceptRequestPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Administrator reviews and accepts a justified request.
    Sets status to ACCEPTED or CORRECTION_PENDING (if database record update is pending).
    Acceptance alone does not falsely mark records as corrected.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ? AND assigned_institution_id = ?", (request_id, institution_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        new_status = "CORRECTION_PENDING" if payload.requires_correction else "ACCEPTED"
        old_status = row["status"]

        conn.execute("""
            UPDATE service_requests
            SET status = ?, updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (new_status, request_id))

        # Add remark if provided
        if payload.remarks:
            rem_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO request_remarks (
                    remark_id, request_id, author_user_id, author_name, author_role, message, visibility, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'requester_visible', DATETIME('now', 'localtime'))
            """, (rem_id, request_id, current_user["user_id"], admin_name, user_role, payload.remarks.strip()))

        # Status History
        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=old_status,
            to_status=new_status,
            action="REQUEST_ACCEPTED",
            actor_user_id=current_user["user_id"],
            actor_name=admin_name,
            actor_role=user_role,
            notes=payload.remarks or f"Request accepted by {admin_name}."
        )

        # Notify Requester
        dispatch_notification(
            conn=conn,
            recipient_user_id=row["requester_user_id"],
            institution_id=institution_id,
            title="Request Accepted",
            message=f"Your request '{row['title']}' ({request_id}) has been accepted by the institution. Status: {new_status}.",
            action_url=f"/requests/{request_id}",
            category="service_request",
            priority="normal"
        )

        conn.commit()
        return {"status": "success", "message": f"Request status updated to {new_status}.", "request_id": request_id, "new_status": new_status}
    finally:
        conn.close()


@router.post("/institution/{institution_id}/requests/{request_id}/reject")
def reject_service_request(
    institution_id: str,
    request_id: str,
    payload: RejectRequestPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Administrator rejects an unjustified request with mandatory rejection reason.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ? AND assigned_institution_id = ?", (request_id, institution_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        reason = payload.rejection_reason.strip()
        old_status = row["status"]

        conn.execute("""
            UPDATE service_requests
            SET status = 'REJECTED',
                rejection_reason = ?,
                resolved_at = DATETIME('now', 'localtime'),
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (reason, request_id))

        # Add remark to thread
        rem_msg = f"Official Rejection Reason: {reason}"
        if payload.remarks:
            rem_msg += f"\nAdditional remarks: {payload.remarks.strip()}"

        rem_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO request_remarks (
                remark_id, request_id, author_user_id, author_name, author_role, message, visibility, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'requester_visible', DATETIME('now', 'localtime'))
        """, (rem_id, request_id, current_user["user_id"], admin_name, user_role, rem_msg))

        # Status History
        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=old_status,
            to_status="REJECTED",
            action="REQUEST_REJECTED",
            actor_user_id=current_user["user_id"],
            actor_name=admin_name,
            actor_role=user_role,
            notes=reason
        )

        # Notify Requester
        dispatch_notification(
            conn=conn,
            recipient_user_id=row["requester_user_id"],
            institution_id=institution_id,
            title="Request Rejected",
            message=f"Your request '{row['title']}' ({request_id}) was reviewed and rejected. Reason: {reason}",
            action_url=f"/requests/{request_id}",
            category="service_request",
            priority="high"
        )

        conn.commit()
        return {
            "status": "success",
            "request_status": "REJECTED",
            "new_status": "REJECTED",
            "message": "Request rejected successfully.",
            "request_id": request_id,
            "rejection_reason": reason
        }
    finally:
        conn.close()


@router.post("/institution/{institution_id}/requests/{request_id}/request-clarification")
def request_clarification(
    institution_id: str,
    request_id: str,
    payload: ClarificationPromptPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Administrator requests additional evidence, proof, or clarification from the requester.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ? AND assigned_institution_id = ?", (request_id, institution_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        prompt = payload.clarification_prompt.strip()
        old_status = row["status"]

        conn.execute("""
            UPDATE service_requests
            SET status = 'CLARIFICATION_REQUIRED',
                clarification_prompt = ?,
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (prompt, request_id))

        # Add remark to thread
        rem_msg = f"Action Required: Clarification Requested: {prompt}"
        if payload.remarks:
            rem_msg += f"\nRemarks: {payload.remarks.strip()}"

        rem_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO request_remarks (
                remark_id, request_id, author_user_id, author_name, author_role, message, visibility, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'requester_visible', DATETIME('now', 'localtime'))
        """, (rem_id, request_id, current_user["user_id"], admin_name, user_role, rem_msg))

        # Status History
        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=old_status,
            to_status="CLARIFICATION_REQUIRED",
            action="CLARIFICATION_REQUESTED",
            actor_user_id=current_user["user_id"],
            actor_name=admin_name,
            actor_role=user_role,
            notes=prompt
        )

        # Notify Requester
        dispatch_notification(
            conn=conn,
            recipient_user_id=row["requester_user_id"],
            institution_id=institution_id,
            title="Action Required: Clarification Requested",
            message=f"Administrator requested clarification for '{row['title']}': {prompt}",
            action_url=f"/requests/{request_id}",
            category="service_request",
            priority="high"
        )

        conn.commit()
        return {
            "status": "success",
            "request_status": "CLARIFICATION_REQUIRED",
            "new_status": "CLARIFICATION_REQUIRED",
            "message": "Clarification request sent to requester.",
            "request_id": request_id
        }
    finally:
        conn.close()


@router.post("/institution/{institution_id}/requests/{request_id}/remarks")
def add_institution_remark(
    institution_id: str,
    request_id: str,
    payload: AddRemarkPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Administrator adds a remark.
    Can be marked requester_visible (seen by requester) or internal_only (strictly confidential).
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ? AND assigned_institution_id = ?", (request_id, institution_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        visibility = payload.visibility if payload.visibility in ("requester_visible", "internal_only") else "requester_visible"
        msg = payload.message.strip()

        rem_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO request_remarks (
                remark_id, request_id, author_user_id, author_name, author_role, message, visibility, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'))
        """, (rem_id, request_id, current_user["user_id"], admin_name, user_role, msg, visibility))

        conn.execute("UPDATE service_requests SET updated_at = DATETIME('now', 'localtime') WHERE request_id = ?", (request_id,))

        if visibility == "requester_visible":
            dispatch_notification(
                conn=conn,
                recipient_user_id=row["requester_user_id"],
                institution_id=institution_id,
                title="New Remark on Your Request",
                message=f"An administrator posted a remark on request '{row['title']}': {msg[:100]}...",
                action_url=f"/requests/{request_id}",
                category="service_request",
                priority="normal"
            )

        conn.commit()
        return {"status": "success", "remark_id": rem_id, "visibility": visibility}
    finally:
        conn.close()


# ==============================================================================
# 3. RECORD CORRECTION ENGINE (Actual Database Updates with Audit Trail)
# ==============================================================================

@router.post("/institution/{institution_id}/requests/{request_id}/execute-correction")
def execute_record_correction(
    institution_id: str,
    request_id: str,
    payload: ExecuteCorrectionPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Authorised Record Correction Engine.
    Directly updates the original database record (attendance, students, academic_results, users/guardians),
    verifies the change, logs the complete audit trail, and marks the request as CORRECTED.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_id = current_user["user_id"]
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("""
            SELECT * FROM service_requests
            WHERE request_id = ? AND assigned_institution_id = ?
        """, (request_id, institution_id)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        req_dict = dict(row)
        module = (payload.target_module or req_dict.get("target_module") or "").lower().strip()
        record_id = (payload.target_record_id or req_dict.get("target_record_id") or "").strip()
        field = (payload.field_name or req_dict.get("field_name") or "").lower().strip()
        new_val = payload.proposed_new_value.strip()
        remarks = payload.confirmation_remarks.strip()
        evidence_ref = payload.verification_evidence_ref or "Official Institutional Record Review"

        old_val = None
        target_table = None
        actual_record_id = record_id

        # ----------------------------------------------------------------------
        # A. Attendance Record Correction
        # ----------------------------------------------------------------------
        if module in ("attendance", "student_attendance"):
            target_table = "student_attendance"
            psid = req_dict.get("permanent_student_id")
            
            # Find matching attendance record by attendance_id OR (psid and date)
            att_row = conn.execute("""
                SELECT * FROM student_attendance
                WHERE attendance_id = ? OR (permanent_student_id = ? AND attendance_date = ?)
            """, (record_id, psid, record_id)).fetchone()

            if not att_row:
                # If no record exists for that date, create one directly
                old_val = "Not Recorded"
                new_att_id = f"ATT-{uuid.uuid4().hex[:8].upper()}"
                actual_record_id = new_att_id
                conn.execute("""
                    INSERT INTO student_attendance (
                        attendance_id, institution_id, permanent_student_id, academic_year,
                        attendance_date, status, remarks, recorded_by_user_id, created_at, updated_at
                    ) VALUES (?, ?, ?, '2026-2027', ?, ?, ?, ?, DATETIME('now', 'localtime'), DATETIME('now', 'localtime'))
                """, (new_att_id, institution_id, psid, record_id, new_val.lower(), f"Corrected via {request_id}: {remarks}", admin_id))
            else:
                old_val = att_row["status"]
                actual_record_id = att_row["attendance_id"]
                conn.execute("""
                    UPDATE student_attendance
                    SET status = ?, remarks = ?, updated_at = DATETIME('now', 'localtime'), recorded_by_user_id = ?
                    WHERE attendance_id = ?
                """, (new_val.lower(), f"Corrected via {request_id}: {remarks}", admin_id, actual_record_id))

        # ----------------------------------------------------------------------
        # B. Student Profile / Personal Information Correction
        # ----------------------------------------------------------------------
        elif module in ("student_profile", "student_personal", "personal_info", "students"):
            target_table = "students"
            st_id = req_dict.get("affected_student_id")
            psid = req_dict.get("permanent_student_id")
            
            st_row = conn.execute("""
                SELECT * FROM students
                WHERE student_id = ? OR permanent_student_id = ?
            """, (st_id, psid)).fetchone()

            if not st_row:
                raise HTTPException(status_code=404, detail="Target student record not found.")

            actual_record_id = st_row["student_id"]

            # Map field to actual column
            field_col = field.replace(" ", "_")
            if field_col in ("name", "full_name"): field_col = "student_name"
            if field_col in ("dob",): field_col = "date_of_birth"

            if field_col not in ("student_name", "date_of_birth", "gender", "first_language"):
                raise HTTPException(status_code=400, detail=f"Unsupported field '{field_col}' for student record correction.")

            old_val = str(st_row[field_col] or "")
            conn.execute(f"""
                UPDATE students
                SET {field_col} = ?
                WHERE student_id = ?
            """, (new_val, actual_record_id))

        # ----------------------------------------------------------------------
        # C. Examination Marks / Results Correction
        # ----------------------------------------------------------------------
        elif module in ("examination_marks", "examination_results", "academic_results"):
            target_table = "academic_results"
            
            # Find result by result_id OR permanent_student_id + subject_name
            res_row = conn.execute("""
                SELECT * FROM academic_results
                WHERE result_id = ? OR (permanent_student_id = ? AND subject_name = ?)
            """, (record_id, req_dict.get("permanent_student_id"), req_dict.get("field_name"))).fetchone()

            if not res_row:
                raise HTTPException(status_code=404, detail=f"Examination result record '{record_id}' not found.")

            actual_record_id = res_row["result_id"]
            old_val = str(res_row["marks_obtained"])
            max_marks = float(res_row["maximum_marks"] or 100.0)
            
            try:
                new_marks_float = float(new_val)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Marks must be a valid number, got '{new_val}'.")

            new_pct = round((new_marks_float / max_marks) * 100, 2)
            new_grade = "A+" if new_pct >= 90 else "A" if new_pct >= 80 else "B+" if new_pct >= 70 else "B" if new_pct >= 60 else "C" if new_pct >= 50 else "D" if new_pct >= 35 else "F"

            conn.execute("""
                UPDATE academic_results
                SET marks_obtained = ?, percentage = ?, grade = ?, updated_at = DATETIME('now', 'localtime'), recorded_by_user_id = ?
                WHERE result_id = ?
            """, (new_marks_float, new_pct, new_grade, admin_id, actual_record_id))

            # Audit in academic_result_audits
            aud_id = f"AUD-RES-{uuid.uuid4().hex[:8].upper()}"
            conn.execute("""
                INSERT INTO academic_result_audits (
                    audit_id, result_id, previous_marks, new_marks, previous_max_marks,
                    new_max_marks, reason_for_change, modified_by_user_id, modified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'))
            """, (aud_id, actual_record_id, float(old_val), new_marks_float, max_marks, max_marks, remarks, admin_id))

        # ----------------------------------------------------------------------
        # D. Parent / Guardian / Contact Information Correction
        # ----------------------------------------------------------------------
        elif module in ("parent_info", "guardian_info", "contact_info", "users", "guardians"):
            target_table = "guardians"
            req_uid = req_dict["requester_user_id"]
            
            g_row = conn.execute("SELECT * FROM guardians WHERE user_id = ? OR guardian_id = ?", (req_uid, record_id)).fetchone()
            if not g_row:
                raise HTTPException(status_code=404, detail="Target guardian record not found.")

            actual_record_id = g_row["guardian_id"]
            field_col = field.replace(" ", "_")
            if field_col not in ("phone", "email", "address", "full_name"):
                raise HTTPException(status_code=400, detail=f"Unsupported field '{field_col}' for guardian record correction.")

            old_val = str(g_row[field_col] or "")
            conn.execute(f"UPDATE guardians SET {field_col} = ? WHERE guardian_id = ?", (new_val, actual_record_id))
            
            # Also sync users table if phone or email or full_name
            if field_col in ("phone", "email", "full_name"):
                conn.execute(f"UPDATE users SET {field_col} = ? WHERE user_id = ?", (new_val, g_row["user_id"]))

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported target module '{module}'.")

        # ----------------------------------------------------------------------
        # Record into request_corrections
        # ----------------------------------------------------------------------
        corr_id = f"CORR-{uuid.uuid4().hex[:8].upper()}"
        conn.execute("""
            INSERT INTO request_corrections (
                correction_id, request_id, target_table, target_record_id, field_name,
                previous_value, corrected_value, correction_reason, administrator_id,
                administrator_name, administrator_role, verification_status, verified_by_user_id, verified_at, created_at
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, 'VERIFIED', ?, DATETIME('now', 'localtime'), DATETIME('now', 'localtime')
            )
        """, (
            corr_id, request_id, target_table, actual_record_id, field,
            old_val, new_val, remarks, admin_id,
            admin_name, user_role, admin_id
        ))

        # Transition request status to CORRECTED
        old_status = req_dict["status"]
        conn.execute("""
            UPDATE service_requests
            SET status = 'CORRECTED',
                current_value = ?,
                resolved_at = DATETIME('now', 'localtime'),
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (new_val, request_id))

        # Status History
        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=old_status,
            to_status="CORRECTED",
            action="RECORD_CORRECTED",
            actor_user_id=admin_id,
            actor_name=admin_name,
            actor_role=user_role,
            notes=f"Authorized record correction: Changed '{field}' in {target_table} from '{old_val}' to '{new_val}'. Remarks: {remarks}"
        )

        # Audit Log
        add_audit_log(
            conn=conn,
            request_id=request_id,
            actor_user_id=admin_id,
            actor_role=user_role,
            action="RECORD_CORRECTION_EXECUTED",
            entity_type=target_table,
            entity_id=actual_record_id,
            school_id=institution_id,
            details={
                "target_table": target_table,
                "field_name": field,
                "previous_value": old_val,
                "corrected_value": new_val,
                "correction_reason": remarks,
                "evidence_ref": evidence_ref
            }
        )

        # Unified Student Record Audit Trail
        try:
            target_student_id = req_dict.get("affected_student_id")
            target_psid = req_dict.get("permanent_student_id")
            if not target_psid and actual_record_id:
                s_check = conn.execute("SELECT student_id, permanent_student_id FROM students WHERE student_id = ? OR permanent_student_id = ?", (actual_record_id, actual_record_id)).fetchone()
                if s_check:
                    target_student_id = s_check["student_id"]
                    target_psid = s_check["permanent_student_id"]
            if target_student_id and target_psid:
                conn.execute("""
                    INSERT INTO student_record_audits (
                        audit_id, student_id, permanent_student_id, institution_id,
                        admin_user_id, admin_name, field_modified, previous_value,
                        updated_value, reason, source, request_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'))
                """, (
                    f"AUD-{uuid.uuid4().hex[:12].upper()}", target_student_id, target_psid, institution_id,
                    admin_id, admin_name, field, str(old_val), str(new_val), remarks,
                    "Approved Correction Request", request_id
                ))
        except Exception as audit_err:
            print(f"[Warning] Failed to write unified student_record_audit from request: {audit_err}")

        # Notify Requester
        dispatch_notification(
            conn=conn,
            recipient_user_id=req_dict["requester_user_id"],
            institution_id=institution_id,
            title="Record Correction Verified & Completed",
            message=f"Your request '{req_dict['title']}' ({request_id}) has been successfully investigated and corrected in the official database. Previous: '{old_val}' -> Corrected: '{new_val}'.",
            action_url=f"/requests/{request_id}",
            category="service_request",
            priority="high"
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Authorized record correction executed successfully and saved to official database.",
            "correction_id": corr_id,
            "request_id": request_id,
            "target_table": target_table,
            "target_record_id": actual_record_id,
            "field_name": field,
            "previous_value": old_val,
            "corrected_value": new_val,
            "verification_status": "VERIFIED",
            "verified": True,
            "request_status": "CORRECTED",
            "updated_request_status": "CORRECTED"
        }
    finally:
        conn.close()


@router.post("/institution/{institution_id}/requests/{request_id}/close")
def close_service_request(
    institution_id: str,
    request_id: str,
    payload: Optional[Dict[str, Any]] = Body(default={}),
    current_user: dict = Depends(get_current_user)
):
    """
    Administrator marks request as CLOSED after verification.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ? AND assigned_institution_id = ?", (request_id, institution_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        closing_notes = (payload and payload.get("closing_remarks")) or "Request closed after complete resolution and verification."

        conn.execute("""
            UPDATE service_requests
            SET status = 'CLOSED',
                closed_at = DATETIME('now', 'localtime'),
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (request_id,))

        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=row["status"],
            to_status="CLOSED",
            action="REQUEST_CLOSED",
            actor_user_id=current_user["user_id"],
            actor_name=admin_name,
            actor_role=user_role,
            notes=closing_notes
        )

        dispatch_notification(
            conn=conn,
            recipient_user_id=row["requester_user_id"],
            institution_id=institution_id,
            title="Request Closed",
            message=f"Your request '{row['title']}' ({request_id}) has been formally verified and closed.",
            action_url=f"/requests/{request_id}",
            category="service_request",
            priority="normal"
        )

        conn.commit()
        return {"status": "success", "message": "Request closed successfully.", "request_id": request_id, "new_status": "CLOSED"}
    finally:
        conn.close()


@router.post("/institution/{institution_id}/requests/{request_id}/escalate")
def escalate_service_request(
    institution_id: str,
    request_id: str,
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Institution Administrator escalates an unresolved or platform-level request to the Platform Administrator.
    """
    conn = get_connection()
    try:
        user_role = current_user["role"]
        user_school = current_user.get("school_id")
        admin_name = current_user.get("full_name") or "Administrator"

        if user_role != "platform_admin" and user_school != institution_id:
            raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ? AND assigned_institution_id = ?", (request_id, institution_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found in this institution.")

        reason = payload.get("reason", "Escalated for platform administrator review.")

        conn.execute("""
            UPDATE service_requests
            SET is_escalated = 1,
                escalated_to = 'platform',
                escalated_at = DATETIME('now', 'localtime'),
                routing_tier = 'platform',
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (request_id,))

        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=row["status"],
            to_status=row["status"],
            action="REQUEST_ESCALATED",
            actor_user_id=current_user["user_id"],
            actor_name=admin_name,
            actor_role=user_role,
            notes=f"Escalated to Platform Administrator. Reason: {reason}"
        )

        dispatch_notification(
            conn=conn,
            recipient_role="platform_admin",
            title=f"Request Escalated ({request_id})",
            message=f"Institution {institution_id} escalated request '{row['title']}'. Reason: {reason}",
            action_url=f"/admin/requests?request_id={request_id}",
            category="service_request",
            priority="high"
        )

        conn.commit()
        return {"status": "success", "message": "Request escalated to Platform Administrator.", "request_id": request_id}
    finally:
        conn.close()


# ==============================================================================
# 4. PLATFORM ADMINISTRATOR APIS
# ==============================================================================

@router.get("/admin/requests/oversight")
def platform_request_oversight(
    institution_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    is_escalated: Optional[int] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Platform Administrator Oversight:
    View escalated requests, institution summaries, search by Request ID / Student ID,
    filter by institution, and review institution decisions.
    """
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform administrator access required.")

    conn = get_connection()
    try:
        where_clauses = ["1=1"]
        params = []

        if institution_id and institution_id.lower() != "all":
            where_clauses.append("sr.assigned_institution_id = ?")
            params.append(institution_id)

        if status_filter and status_filter.upper() != "ALL":
            where_clauses.append("sr.status = ?")
            params.append(status_filter.upper())

        if category and category.lower() != "all":
            where_clauses.append("sr.category = ?")
            params.append(category)

        if is_escalated is not None:
            where_clauses.append("sr.is_escalated = ?")
            params.append(is_escalated)

        if search:
            search_pattern = f"%{search.strip()}%"
            where_clauses.append("(sr.request_id LIKE ? OR sr.tracking_number LIKE ? OR sr.title LIKE ? OR sr.affected_student_id LIKE ? OR sr.permanent_student_id LIKE ? OR sr.requester_name LIKE ?)")
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        where_sql = " AND ".join(where_clauses)
        rows = conn.execute(f"""
            SELECT sr.*, s.school_name AS institution_name, s.school_type
            FROM service_requests sr
            LEFT JOIN schools s ON s.school_id = sr.assigned_institution_id
            WHERE {where_sql}
            ORDER BY sr.submitted_at DESC
        """, tuple(params)).fetchall()

        # Summary KPIs
        total_all = conn.execute("SELECT count(*) FROM service_requests").fetchone()[0]
        total_escalated = conn.execute("SELECT count(*) FROM service_requests WHERE is_escalated = 1").fetchone()[0]
        total_open = conn.execute("SELECT count(*) FROM service_requests WHERE status NOT IN ('REJECTED', 'CLOSED')").fetchone()[0]
        total_corrected = conn.execute("SELECT count(*) FROM service_requests WHERE status IN ('CORRECTED', 'VERIFIED')").fetchone()[0]

        inst_breakdown = conn.execute("""
            SELECT sr.assigned_institution_id, s.school_name, count(*) as count
            FROM service_requests sr
            LEFT JOIN schools s ON s.school_id = sr.assigned_institution_id
            WHERE sr.assigned_institution_id IS NOT NULL
            GROUP BY sr.assigned_institution_id
            ORDER BY count DESC
        """).fetchall()

        kpis = {
            "total": total_all,
            "escalated": total_escalated,
            "open": total_open,
            "corrected": total_corrected,
            "total_requests": total_all,
            "escalated_requests": total_escalated,
            "open_requests": total_open,
            "corrected_requests": total_corrected
        }

        return {
            "kpis": kpis,
            "summary": kpis,
            "institution_breakdown": [dict(ib) for ib in inst_breakdown],
            "total_matching": len(rows),
            "requests": [dict(r) for r in rows]
        }
    finally:
        conn.close()


@router.post("/admin/requests/{request_id}/forward")
def platform_forward_request(
    request_id: str,
    payload: ForwardRequestPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Platform Administrator forwards/re-assigns a request to the appropriate institution.
    """
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform administrator access required.")

    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Request not found.")

        target_inst = payload.target_institution_id.strip()
        sch_check = conn.execute("SELECT school_name FROM schools WHERE school_id = ?", (target_inst,)).fetchone()
        if not sch_check:
            raise HTTPException(status_code=404, detail=f"Target institution '{target_inst}' not found.")

        old_inst = row["assigned_institution_id"]
        remarks = payload.forward_remarks or f"Forwarded from platform to {sch_check['school_name']} ({target_inst})."

        conn.execute("""
            UPDATE service_requests
            SET assigned_institution_id = ?,
                routing_tier = 'institution',
                updated_at = DATETIME('now', 'localtime')
            WHERE request_id = ?
        """, (target_inst, request_id))

        add_status_history(
            conn=conn,
            request_id=request_id,
            from_status=row["status"],
            to_status=row["status"],
            action="REQUEST_FORWARDED",
            actor_user_id=current_user["user_id"],
            actor_name="Platform Administrator",
            actor_role="platform_admin",
            notes=f"Forwarded from {old_inst or 'Platform'} to {target_inst}. Remarks: {remarks}"
        )

        dispatch_notification(
            conn=conn,
            recipient_role="school_admin",
            institution_id=target_inst,
            title=f"Request Forwarded to Your Institution ({request_id})",
            message=f"Platform Administrator forwarded request '{row['title']}' to your institution desk.",
            action_url=f"/institution/{target_inst}/requests?request_id={request_id}",
            category="service_request",
            priority="normal"
        )

        conn.commit()
        return {
            "status": "success",
            "message": f"Request forwarded to institution {target_inst}.",
            "request_id": request_id,
            "assigned_institution_id": target_inst
        }
    finally:
        conn.close()
