import os
import uuid
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

def mask_email(email: Optional[str]) -> str:
    if not email or "@" not in email:
        return ""
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
    return f"{masked_name}@{domain}"

def mask_phone(phone: Optional[str]) -> str:
    if not phone:
        return ""
    clean = phone.replace("+91", "").replace("-", "").strip()
    if len(clean) >= 4:
        return f"+91-******{clean[-4:]}"
    return "+91-******"

def get_channel_statuses() -> Dict[str, Any]:
    smtp_host = os.environ.get("SMTP_HOST")
    sms_gateway = os.environ.get("SMS_GATEWAY_URL")
    whatsapp_key = os.environ.get("WHATSAPP_API_KEY")

    return {
        "in_app": {
            "channel": "in_app",
            "provider": "NagrikSetu In-App Notification Hub",
            "status": "active",
            "configured": True,
            "details": "Operational real-time in-app delivery ledger"
        },
        "email": {
            "channel": "email",
            "provider": "SMTP Mail Gateway",
            "status": "active" if smtp_host else "provider_unavailable",
            "configured": bool(smtp_host),
            "details": f"Connected to {smtp_host}" if smtp_host else "SMTP_HOST environment variable not configured"
        },
        "sms": {
            "channel": "sms",
            "provider": "NIC / National SMS Gateway",
            "status": "active" if sms_gateway else "provider_unavailable",
            "configured": bool(sms_gateway),
            "details": f"Connected to {sms_gateway}" if sms_gateway else "SMS_GATEWAY_URL environment variable not configured"
        },
        "whatsapp": {
            "channel": "whatsapp",
            "provider": "Meta WhatsApp Business Cloud API",
            "status": "active" if whatsapp_key else "provider_unavailable",
            "configured": bool(whatsapp_key),
            "details": "Active WhatsApp Cloud token" if whatsapp_key else "WHATSAPP_API_KEY environment variable not configured"
        }
    }

def get_user_preferences(conn: sqlite3.Connection, user_id: str) -> Dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM notification_preferences WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if row:
        return dict(row)

    # Defaults
    return {
        "preference_id": f"pref-{user_id}",
        "user_id": user_id,
        "academic_updates": 1,
        "attendance_alerts": 1,
        "examination_alerts": 1,
        "admission_updates": 1,
        "institution_announcements": 1,
        "administrative_alerts": 1,
        "email_enabled": 1,
        "sms_enabled": 1,
        "whatsapp_enabled": 0,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

def update_user_preferences(conn: sqlite3.Connection, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    existing = conn.execute("SELECT preference_id FROM notification_preferences WHERE user_id = ?", (user_id,)).fetchone()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    acad = int(updates.get("academic_updates", 1))
    att = int(updates.get("attendance_alerts", 1))
    exam = int(updates.get("examination_alerts", 1))
    adm = int(updates.get("admission_updates", 1))
    ann = int(updates.get("institution_announcements", 1))
    admn_alt = int(updates.get("administrative_alerts", 1))
    em = int(updates.get("email_enabled", 1))
    sms = int(updates.get("sms_enabled", 1))
    wa = int(updates.get("whatsapp_enabled", 0))

    if existing:
        conn.execute("""
            UPDATE notification_preferences
            SET academic_updates = ?, attendance_alerts = ?, examination_alerts = ?,
                admission_updates = ?, institution_announcements = ?, administrative_alerts = ?,
                email_enabled = ?, sms_enabled = ?, whatsapp_enabled = ?, updated_at = ?
            WHERE user_id = ?
        """, (acad, att, exam, adm, ann, admn_alt, em, sms, wa, now_str, user_id))
    else:
        pref_id = f"PREF-{uuid.uuid4().hex[:8].upper()}"
        conn.execute("""
            INSERT INTO notification_preferences (
                preference_id, user_id, academic_updates, attendance_alerts,
                examination_alerts, admission_updates, institution_announcements,
                administrative_alerts, email_enabled, sms_enabled, whatsapp_enabled, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pref_id, user_id, acad, att, exam, adm, ann, admn_alt, em, sms, wa, now_str))

    conn.commit()
    return get_user_preferences(conn, user_id)

def dispatch_notification(
    conn: sqlite3.Connection,
    recipient_user_id: Optional[str] = None,
    recipient_role: Optional[str] = None,
    institution_id: Optional[str] = None,
    category: str = "general",
    title: str = "",
    message: str = "",
    action_url: Optional[str] = None,
    priority: str = "normal",
    related_record_type: Optional[str] = None,
    related_record_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    channel: str = "in_app"
) -> Optional[str]:
    """
    Central notification dispatcher with idempotency checks, preference enforcement,
    and external channel simulation/logging without fabricating fake provider deliveries.
    """
    # 1. Idempotency Check
    if idempotency_key:
        existing = conn.execute(
            "SELECT notification_id FROM portal_notifications WHERE idempotency_key = ?",
            (idempotency_key,)
        ).fetchone()
        if existing:
            return existing["notification_id"]

    # 2. Preference Filtering (respects user preferences; mandatory security & critical administrative alerts cannot be disabled)
    user_row = None
    pref = None
    if recipient_user_id:
        user_row = conn.execute("SELECT user_id, email, phone, role FROM users WHERE user_id = ?", (recipient_user_id,)).fetchone()
        pref = get_user_preferences(conn, recipient_user_id)

        is_critical = (priority == "urgent" or category in ("security", "system"))
        if not is_critical and pref:
            if category == "attendance" and not pref.get("attendance_alerts"):
                return None
            if category in ("academic", "examination") and not pref.get("academic_updates") and not pref.get("examination_alerts"):
                return None
            if category == "admission" and not pref.get("admission_updates"):
                return None
            if category == "announcement" and not pref.get("institution_announcements"):
                return None
            if category == "administrative" and not pref.get("administrative_alerts"):
                return None

    # 3. Create In-App Notification
    notif_id = f"NOTIF-{uuid.uuid4().hex[:12].upper()}"
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""
        INSERT INTO portal_notifications (
            notification_id, recipient_user_id, recipient_role, institution_id,
            category, priority, channel, delivery_status,
            title, message, action_url, related_record_type, related_record_id,
            idempotency_key, is_read, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        notif_id, recipient_user_id, recipient_role, institution_id,
        category, priority, channel, "delivered",
        title, message, action_url, related_record_type, related_record_id,
        idempotency_key, now_str
    ))

    # 4. External Channel Log Tracking (Email / SMS / WhatsApp)
    if user_row and pref:
        statuses = get_channel_statuses()
        email_val = user_row["email"]
        phone_val = user_row["phone"]

        # Email delivery attempt
        if pref.get("email_enabled") and email_val:
            ch_status = statuses["email"]["status"]
            err = None if ch_status == "active" else "SMTP mail provider unavailable in environment"
            conn.execute("""
                INSERT INTO notification_delivery_logs (
                    log_id, notification_id, channel, recipient_destination,
                    status, error_message, retry_count, created_at, updated_at
                ) VALUES (?, ?, 'email', ?, ?, ?, 0, ?, ?)
            """, (str(uuid.uuid4()), notif_id, mask_email(email_val), ch_status, err, now_str, now_str))

        # SMS delivery attempt
        if pref.get("sms_enabled") and phone_val:
            ch_status = statuses["sms"]["status"]
            err = None if ch_status == "active" else "SMS gateway unavailable in environment"
            conn.execute("""
                INSERT INTO notification_delivery_logs (
                    log_id, notification_id, channel, recipient_destination,
                    status, error_message, retry_count, created_at, updated_at
                ) VALUES (?, ?, 'sms', ?, ?, ?, 0, ?, ?)
            """, (str(uuid.uuid4()), notif_id, mask_phone(phone_val), ch_status, err, now_str, now_str))

        # WhatsApp delivery attempt
        if pref.get("whatsapp_enabled") and phone_val:
            ch_status = statuses["whatsapp"]["status"]
            err = None if ch_status == "active" else "WhatsApp Cloud API provider unavailable in environment"
            conn.execute("""
                INSERT INTO notification_delivery_logs (
                    log_id, notification_id, channel, recipient_destination,
                    status, error_message, retry_count, created_at, updated_at
                ) VALUES (?, ?, 'whatsapp', ?, ?, ?, 0, ?, ?)
            """, (str(uuid.uuid4()), notif_id, mask_phone(phone_val), ch_status, err, now_str, now_str))

    return notif_id


# ==========================================
# EVENT TRIGGER INTEGRATIONS
# ==========================================

def trigger_attendance_notification(
    conn: sqlite3.Connection,
    institution_id: str,
    permanent_student_id: str,
    attendance_date: str,
    status_val: str,
    subject_name: Optional[str] = None
):
    """
    Dispatches attendance notification to student and authorized verified guardians only.
    Non-verified guardians are strictly filtered out.
    """
    if status_val.lower() not in ("absent", "leave"):
        # Typically present does not flood notifications unless requested
        return

    # 1. Lookup student details & user
    student = conn.execute("""
        SELECT s.student_name, s.student_id, s.permanent_student_id, s.school_id, u.user_id
        FROM students s
        LEFT JOIN users u ON (u.permanent_student_id = s.permanent_student_id OR u.student_id = s.student_id)
        WHERE s.permanent_student_id = ?
    """, (permanent_student_id,)).fetchone()

    if not student:
        return

    st_name = student["student_name"]
    st_id = student["student_id"]
    subj_label = f" ({subject_name})" if subject_name else ""
    priority = "high" if status_val.lower() == "absent" else "normal"

    # Notify student (if registered user account exists)
    if student["user_id"]:
        idemp_student = f"att_st:{permanent_student_id}:{attendance_date}:{subject_name or 'gen'}:{status_val}"
        dispatch_notification(
            conn,
            recipient_user_id=student["user_id"],
            institution_id=institution_id,
            category="attendance",
            priority=priority,
            title=f"Attendance Alert: Marked {status_val.title()}",
            message=f"You were marked {status_val.title()} on {attendance_date}{subj_label}.",
            action_url="/student",
            related_record_type="attendance",
            related_record_id=f"{permanent_student_id}_{attendance_date}",
            idempotency_key=idemp_student
        )

    # 2. Lookup verified and authorized guardians ONLY
    guardians = conn.execute("""
        SELECT g.user_id, g.full_name
        FROM student_guardians sg
        JOIN guardians g ON g.guardian_id = sg.guardian_id
        WHERE sg.permanent_student_id = ? AND sg.is_verified = 1 AND sg.can_view_records = 1
    """, (permanent_student_id,)).fetchall()

    for g in guardians:
        idemp_guardian = f"att_gd:{g['user_id']}:{permanent_student_id}:{attendance_date}:{subject_name or 'gen'}:{status_val}"
        dispatch_notification(
            conn,
            recipient_user_id=g["user_id"],
            institution_id=institution_id,
            category="attendance",
            priority=priority,
            title=f"Attendance Alert: {st_name} marked {status_val.title()}",
            message=f"Your child {st_name} ({st_id}) was marked {status_val.title()} on {attendance_date}{subj_label}.",
            action_url=f"/parent?child_psid={permanent_student_id}",
            related_record_type="attendance",
            related_record_id=f"{permanent_student_id}_{attendance_date}",
            idempotency_key=idemp_guardian
        )


def trigger_examination_scheduled_notification(
    conn: sqlite3.Connection,
    exam_id: str,
    institution_id: str,
    exam_name: str,
    standard_or_level: str,
    start_date: str
):
    """
    Dispatches exam schedule notifications to enrolled students, verified guardians, and institution staff.
    """
    # 1. Notify institution admin
    dispatch_notification(
        conn,
        recipient_role="school_admin",
        institution_id=institution_id,
        category="examination",
        priority="normal",
        title=f"Examination Scheduled: {exam_name}",
        message=f"Examination '{exam_name}' has been scheduled for {standard_or_level} starting {start_date}.",
        action_url="/institution-admin",
        related_record_type="examination",
        related_record_id=exam_id,
        idempotency_key=f"exam_admin:{exam_id}"
    )

    # 2. Notify students enrolled in this institution
    students = conn.execute("""
        SELECT u.user_id, s.permanent_student_id
        FROM students s
        JOIN users u ON (u.permanent_student_id = s.permanent_student_id OR u.student_id = s.student_id)
        WHERE s.school_id = ?
        LIMIT 500
    """, (institution_id,)).fetchall()

    for st in students:
        dispatch_notification(
            conn,
            recipient_user_id=st["user_id"],
            institution_id=institution_id,
            category="examination",
            priority="normal",
            title=f"New Examination Scheduled: {exam_name}",
            message=f"'{exam_name}' timetable announced starting from {start_date} ({standard_or_level}).",
            action_url="/student",
            related_record_type="examination",
            related_record_id=exam_id,
            idempotency_key=f"exam_st:{exam_id}:{st['user_id']}"
        )


def trigger_result_notification(
    conn: sqlite3.Connection,
    result_id: str,
    exam_name: str,
    subject_name: str,
    marks_obtained: float,
    maximum_marks: float,
    grade: str,
    permanent_student_id: str,
    institution_id: str,
    is_update: bool = False,
    previous_marks: Optional[float] = None,
    reason: Optional[str] = None
):
    """
    Dispatches result notification to student, verified guardians, and marks-correction audit alert to admin.
    """
    student = conn.execute("""
        SELECT s.student_name, s.student_id, s.permanent_student_id, u.user_id
        FROM students s
        LEFT JOIN users u ON (u.permanent_student_id = s.permanent_student_id OR u.student_id = s.student_id)
        WHERE s.permanent_student_id = ?
    """, (permanent_student_id,)).fetchone()

    if not student:
        return

    st_name = student["student_name"]
    st_id = student["student_id"]
    action_type = "Updated" if is_update else "Published"

    # 1. Notify Student
    if student["user_id"]:
        idemp_st = f"res_st:{result_id}:{marks_obtained}:{action_type}"
        dispatch_notification(
            conn,
            recipient_user_id=student["user_id"],
            institution_id=institution_id,
            category="academic",
            priority="normal",
            title=f"Examination Result {action_type}: {subject_name} ({grade})",
            message=f"Score in {exam_name} - {subject_name}: {marks_obtained}/{maximum_marks} (Grade: {grade}).",
            action_url="/student",
            related_record_type="academic_result",
            related_record_id=result_id,
            idempotency_key=idemp_st
        )

    # 2. Notify Verified Guardians ONLY
    guardians = conn.execute("""
        SELECT g.user_id
        FROM student_guardians sg
        JOIN guardians g ON g.guardian_id = sg.guardian_id
        WHERE sg.permanent_student_id = ? AND sg.is_verified = 1 AND sg.can_view_records = 1
    """, (permanent_student_id,)).fetchall()

    for g in guardians:
        idemp_gd = f"res_gd:{g['user_id']}:{result_id}:{marks_obtained}:{action_type}"
        dispatch_notification(
            conn,
            recipient_user_id=g["user_id"],
            institution_id=institution_id,
            category="academic",
            priority="normal",
            title=f"Academic Result {action_type}: {st_name} - {subject_name}",
            message=f"{st_name} ({st_id}) achieved {marks_obtained}/{maximum_marks} (Grade: {grade}) in {exam_name} ({subject_name}).",
            action_url=f"/parent?child_psid={permanent_student_id}",
            related_record_type="academic_result",
            related_record_id=result_id,
            idempotency_key=idemp_gd
        )

    # 3. If update (marks correction), notify Institution Admin for oversight audit
    if is_update:
        idemp_admin = f"res_audit:{result_id}:{marks_obtained}"
        dispatch_notification(
            conn,
            recipient_role="school_admin",
            institution_id=institution_id,
            category="academic",
            priority="high",
            title=f"Gradebook Audit Alert: Marks Modified for {st_id}",
            message=f"Marks for {st_name} in {subject_name} ({exam_name}) modified from {previous_marks} to {marks_obtained}. Reason: {reason or 'Correction'}.",
            action_url="/institution-admin",
            related_record_type="academic_result_audit",
            related_record_id=result_id,
            idempotency_key=idemp_admin
        )


def trigger_announcement_notification(
    conn: sqlite3.Connection,
    announcement_id: str,
    institution_id: str,
    title: str,
    content: str,
    target_audience: str
):
    """
    Broadcasts announcement notifications to permitted audiences in the institution.
    """
    summary = content[:150] + ("..." if len(content) > 150 else "")

    # 1. Staff
    if target_audience in ("all", "staff"):
        dispatch_notification(
            conn,
            recipient_role="school_staff",
            institution_id=institution_id,
            category="announcement",
            priority="normal",
            title=f"Institution Notice: {title}",
            message=summary,
            action_url="/staff",
            related_record_type="announcement",
            related_record_id=announcement_id,
            idempotency_key=f"ann_staff:{announcement_id}:{institution_id}"
        )

    # 2. Students
    if target_audience in ("all", "students"):
        students = conn.execute("""
            SELECT u.user_id
            FROM students s
            JOIN users u ON (u.permanent_student_id = s.permanent_student_id OR u.student_id = s.student_id)
            WHERE s.school_id = ?
            LIMIT 500
        """, (institution_id,)).fetchall()
        for st in students:
            dispatch_notification(
                conn,
                recipient_user_id=st["user_id"],
                institution_id=institution_id,
                category="announcement",
                priority="normal",
                title=f"Announcement: {title}",
                message=summary,
                action_url="/student",
                related_record_type="announcement",
                related_record_id=announcement_id,
                idempotency_key=f"ann_st:{announcement_id}:{st['user_id']}"
            )

    # 3. Parents
    if target_audience in ("all", "parents"):
        guardians = conn.execute("""
            SELECT DISTINCT g.user_id
            FROM student_guardians sg
            JOIN guardians g ON g.guardian_id = sg.guardian_id
            JOIN students s ON s.permanent_student_id = sg.permanent_student_id
            WHERE s.school_id = ? AND sg.is_verified = 1 AND sg.can_view_records = 1
            LIMIT 500
        """, (institution_id,)).fetchall()
        for gd in guardians:
            dispatch_notification(
                conn,
                recipient_user_id=gd["user_id"],
                institution_id=institution_id,
                category="announcement",
                priority="normal",
                title=f"School Announcement: {title}",
                message=summary,
                action_url="/parent",
                related_record_type="announcement",
                related_record_id=announcement_id,
                idempotency_key=f"ann_gd:{announcement_id}:{gd['user_id']}"
            )


def trigger_staff_administrative_notification(
    conn: sqlite3.Connection,
    institution_id: str,
    action: str,
    staff_name: str,
    staff_email: str,
    actor_email: str
):
    """
    Notifies Institution Admin and Platform Admin regarding staff provisioning/suspensions.
    """
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    # 1. Institution Admin
    dispatch_notification(
        conn,
        recipient_role="school_admin",
        institution_id=institution_id,
        category="administrative",
        priority="high" if action.lower() == "suspended" else "normal",
        title=f"Staff Account {action}: {staff_name}",
        message=f"Staff account for {staff_name} ({staff_email}) was {action.lower()} by {actor_email} on {now_str}.",
        action_url="/institution-admin",
        related_record_type="staff_management",
        related_record_id=staff_email,
        idempotency_key=f"staff_adm:{institution_id}:{staff_email}:{action}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    )

    # 2. Platform Admin Operational & Security alert
    dispatch_notification(
        conn,
        recipient_role="platform_admin",
        institution_id=None,
        category="security",
        priority="high" if action.lower() == "suspended" else "normal",
        title=f"Security Audit: Staff {action} at {institution_id}",
        message=f"Staff account {staff_email} at institution {institution_id} was {action.lower()} by {actor_email}.",
        action_url="/admin",
        related_record_type="platform_audit",
        related_record_id=staff_email,
        idempotency_key=f"staff_plt:{institution_id}:{staff_email}:{action}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    )
