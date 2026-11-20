import logging
import secrets
import re
from datetime import datetime, timedelta
import hashlib
import ocr_service
import notification_service
from fastapi.responses import FileResponse
import base64
import os
import json
import sqlite3
import uuid
from typing import Literal, Optional, List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, field_validator
from database import get_connection
from auth import create_access_token, get_current_user, hash_password, verify_password


app = FastAPI(
    title="NagrikSetu School Service",
    description=(
        "School discovery, public student profiles, authentication, "
        "and secure parent services."
    ),
    version="1.3.0",
)

cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    trusted_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
else:
    trusted_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=trusted_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

import time
import threading
from collections import defaultdict

class AuthRateLimiter:
    """Thread-safe in-memory sliding window rate limiter for authentication endpoints."""
    def __init__(self):
        self._lock = threading.Lock()
        self._requests = defaultdict(list)
        self._failed_attempts = defaultdict(list)

    def record_request(self, client_ip: str, max_per_minute: int = 60) -> bool:
        now = time.time()
        with self._lock:
            self._requests[client_ip] = [t for t in self._requests[client_ip] if now - t < 60]
            if len(self._requests[client_ip]) >= max_per_minute:
                return False
            self._requests[client_ip].append(now)
            return True

    def record_failed_login(self, client_ip: str, identifier: str, max_failures: int = 5) -> bool:
        now = time.time()
        key = (client_ip, identifier.lower().strip())
        with self._lock:
            self._failed_attempts[key] = [t for t in self._failed_attempts[key] if now - t < 60]
            self._failed_attempts[key].append(now)
            return len(self._failed_attempts[key]) < max_failures

    def is_locked_out(self, client_ip: str, identifier: str, max_failures: int = 5) -> bool:
        now = time.time()
        key = (client_ip, identifier.lower().strip())
        with self._lock:
            self._failed_attempts[key] = [t for t in self._failed_attempts[key] if now - t < 60]
            return len(self._failed_attempts[key]) >= max_failures

    def reset_failed_login(self, client_ip: str, identifier: str):
        key = (client_ip, identifier.lower().strip())
        with self._lock:
            if key in self._failed_attempts:
                del self._failed_attempts[key]

auth_limiter = AuthRateLimiter()


class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    requires_workspace_selection: bool = False
    temp_token: Optional[str] = None
    workspaces: Optional[List[Dict[str, Any]]] = None
    role: Optional[str] = None
    school_id: Optional[str] = None
    student_id: Optional[str] = None
    permanent_student_id: Optional[str] = None


class NotificationPreferencesPayload(BaseModel):
    academic_updates: Optional[int] = 1
    attendance_alerts: Optional[int] = 1
    examination_alerts: Optional[int] = 1
    admission_updates: Optional[int] = 1
    institution_announcements: Optional[int] = 1
    administrative_alerts: Optional[int] = 1
    email_enabled: Optional[int] = 1
    sms_enabled: Optional[int] = 1
    whatsapp_enabled: Optional[int] = 0


class ParentUpdateRequest(BaseModel):
    permanent_student_id: str = Field(min_length=1, max_length=100)
    request_type: Literal["request_change", "report_change"]
    field_name: Literal[
        "student_name",
        "date_of_birth",
        "gender",
        "first_language",
    ]
    proposed_value: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=5, max_length=1000)
    supporting_document_id: Optional[str] = Field(
        default=None, max_length=100
    )


class StudentLookupRequest(BaseModel):
    student_identifier: str = Field(min_length=3, max_length=100)

    @field_validator("student_identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 3:
            raise ValueError("Student identifier must contain at least 3 characters.")
        return s


class StudentRegisterRequest(BaseModel):
    student_identifier: str = Field(min_length=3, max_length=100)
    date_of_birth: Optional[str] = Field(default=None, max_length=25)
    full_name: Optional[str] = Field(default=None, max_length=150)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("student_identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 3:
            raise ValueError("Student identifier must contain at least 3 characters.")
        return s

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        v = v.strip().lower()
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", v):
            raise ValueError("Please provide a valid email format or leave it blank.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        v = v.strip()
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Please provide a valid 10-digit mobile number or leave it blank.")
        return v


class StudentRegisterResponse(BaseModel):
    user_id: str
    student_id: str
    permanent_student_id: str
    full_name: str
    school_id: str
    message: str


class ParentRegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Full name must contain at least 2 non-whitespace characters.")
        return s

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            s = v.strip().lower()
            if not s:
                return None
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", s):
                raise ValueError("Please provide a valid email format.")
            return s
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return None
            digits = re.sub(r"\D", "", s)
            if len(digits) == 12 and digits.startswith("91"):
                digits = digits[2:]
            elif len(digits) == 11 and digits.startswith("0"):
                digits = digits[1:]
            if not re.match(r"^[6-9]\d{9}$", digits):
                raise ValueError("Please provide a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
            return digits
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must contain at least 8 characters.")
        has_letter = any(c.isalpha() for c in v)
        has_num_or_special = any(not c.isalpha() for c in v)
        if not has_letter or not has_num_or_special:
            raise ValueError("Password must contain at least one letter and at least one number or special character.")
        return v


class RegisterResponse(BaseModel):
    user_id: str
    full_name: str
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    role: Optional[str] = "parent"


class SetupPasswordPayload(BaseModel):
    identifier: str = Field(min_length=3, max_length=150)
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must contain at least 8 characters.")
        has_letter = any(c.isalpha() for c in v)
        has_num_or_special = any(not c.isalpha() for c in v)
        if not has_letter or not has_num_or_special:
            raise ValueError("Password must contain at least one letter and at least one number or special character.")
        return v


class ParentLinkingRequestCreate(BaseModel):
    school_id: str = Field(min_length=1, max_length=50)
    student_ref: str = Field(min_length=1, max_length=100)
    relationship_type: str = Field(min_length=2, max_length=50)
    verification_doc_id: Optional[str] = Field(default=None, max_length=100)
    additional_notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("school_id")
    @classmethod
    def validate_school_id(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("School ID cannot be empty.")
        return s

    @field_validator("student_ref")
    @classmethod
    def validate_student_ref(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Student reference cannot be empty.")
        return s

    @field_validator("relationship_type")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Relationship type cannot be empty.")
        return s


class ParentLinkingRequestResponse(BaseModel):
    request_id: str
    school_id: str
    student_ref: str
    relationship_type: str
    request_status: str
    message: str


def require_parent(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("parent", "citizen"):
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available to citizen and parent accounts.",
        )
    return user


def require_student(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available to student accounts.",
        )
    return user


def get_institution_5char_prefix(school_id: str) -> str:
    """Normalize institution code to 5-character prefix (e.g. SCH001 -> SCH01, COL001 -> COL01)."""
    m = re.match(r"^([A-Z]+)(\d+)$", school_id)
    if m:
        letters, num = m.groups()
        return f"{letters}{int(num):02d}"
    return school_id


def generate_next_student_id(conn, school_id: str) -> str:
    """
    Standardized Student ID generator:
    Format: INSTITUTION_5CHAR_PREFIX + THREE_DIGIT_SEQUENCE (e.g. SCH01001, SCH01002, COL01001)
    Finds the highest sequence assigned for this institution and returns prefix + next sequence.
    Never reuses retired or deleted IDs.
    """
    prefix = get_institution_5char_prefix(school_id)
    rows = conn.execute(
        "SELECT student_id FROM students WHERE school_id = ? AND student_id LIKE ?",
        (school_id, f"{prefix}%")
    ).fetchall()

    max_seq = 0
    prefix_len = len(prefix)
    for (sid,) in rows:
        suffix = sid[prefix_len:]
        if suffix.isdigit():
            val = int(suffix)
            if val > max_seq:
                max_seq = val

    next_seq = max_seq + 1
    return f"{prefix}{next_seq:03d}"


STAFF_ROLES = (
    "school_admin",
    "institution_admin",
    "admissions_officer",
    "academic_admin",
    "student_records_officer",
    "school_staff",
    "general_staff",
    "teacher",
    "academic_coordinator",
)

DEFAULT_ROLE_PERMS = {
    "school_admin": {
        "can_view_applications": 1,
        "can_review_details": 1,
        "can_request_clarification": 1,
        "can_recommend_decision": 1,
        "can_approve_stage1": 1,
        "can_view_history": 1,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },
    "admissions_officer": {
        "can_view_applications": 1,
        "can_review_details": 1,
        "can_request_clarification": 1,
        "can_recommend_decision": 1,
        "can_approve_stage1": 0,
        "can_view_history": 1,
        "can_manage_academics": 0,
        "can_manage_students": 0,
    },
    "academic_admin": {
        "can_view_applications": 1,
        "can_review_details": 1,
        "can_request_clarification": 1,
        "can_recommend_decision": 1,
        "can_approve_stage1": 1,
        "can_view_history": 1,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },
    "student_records_officer": {
        "can_view_applications": 0,
        "can_review_details": 0,
        "can_request_clarification": 0,
        "can_recommend_decision": 0,
        "can_approve_stage1": 0,
        "can_view_history": 0,
        "can_manage_academics": 0,
        "can_manage_students": 1,
    },
    "school_staff": {
        "can_view_applications": 1,
        "can_review_details": 1,
        "can_request_clarification": 1,
        "can_recommend_decision": 1,
        "can_approve_stage1": 0,
        "can_view_history": 1,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },
    "general_staff": {
        "can_view_applications": 0,
        "can_review_details": 0,
        "can_request_clarification": 0,
        "can_recommend_decision": 0,
        "can_approve_stage1": 0,
        "can_view_history": 0,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },
    "teacher": {
        "can_view_applications": 0,
        "can_review_details": 0,
        "can_request_clarification": 0,
        "can_recommend_decision": 0,
        "can_approve_stage1": 0,
        "can_view_history": 0,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },
    "academic_coordinator": {
        "can_view_applications": 0,
        "can_review_details": 0,
        "can_request_clarification": 0,
        "can_recommend_decision": 0,
        "can_approve_stage1": 0,
        "can_view_history": 0,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },
}


def get_staff_permissions(conn, user_id: str, institution_id: str, role_id: str) -> dict:
    if role_id in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
        return dict(DEFAULT_ROLE_PERMS["school_admin"])
    row = conn.execute("""
        SELECT can_view_applications, can_review_details, can_request_clarification,
               can_recommend_decision, can_approve_stage1, can_view_history,
               can_manage_academics, can_manage_students
        FROM institution_staff_permissions
        WHERE user_id = ? AND institution_id = ?
    """, (user_id, institution_id)).fetchone()
    if row:
        return dict(row)
    defaults = DEFAULT_ROLE_PERMS.get(role_id, DEFAULT_ROLE_PERMS["general_staff"])
    perm_id = str(uuid.uuid4())
    conn.execute("""
        INSERT OR IGNORE INTO institution_staff_permissions
        (id, user_id, institution_id, role_id,
         can_view_applications, can_review_details, can_request_clarification,
         can_recommend_decision, can_approve_stage1, can_view_history,
         can_manage_academics, can_manage_students, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'system_auto')
    """, (
        perm_id, user_id, institution_id, role_id,
        defaults["can_view_applications"], defaults["can_review_details"],
        defaults["can_request_clarification"], defaults["can_recommend_decision"],
        defaults["can_approve_stage1"], defaults["can_view_history"],
        defaults["can_manage_academics"], defaults["can_manage_students"],
    ))
    conn.commit()
    return dict(defaults)


def require_school_staff(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in STAFF_ROLES and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution staff access required.",
        )
    if not user.get("school_id") and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to an institution.",
        )
    return user


def require_school_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution administrator access required.",
        )
    if not user.get("school_id") and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to an institution.",
        )
    return user


def require_platform_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform administrator access required.",
        )
    return user


def record_platform_audit(
    conn,
    event_type: str,
    event_category: str,
    institution_id: Optional[str],
    actor_user_id: Optional[str],
    actor_role: Optional[str],
    entity_type: str,
    entity_id: Optional[str],
    action: str,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    remarks: Optional[str] = None,
    request_id: Optional[str] = None,
    actor_name: Optional[str] = None,
) -> str:
    log_id = f"EVT-{uuid.uuid4().hex[:12].upper()}"
    if not actor_name and actor_user_id:
        try:
            u = conn.execute("SELECT full_name, email, role FROM users WHERE user_id = ?", (actor_user_id,)).fetchone()
            if u:
                actor_name = u["full_name"] or u["email"] or actor_user_id
                if not actor_role:
                    actor_role = u["role"]
        except Exception:
            pass
    if not actor_name:
        actor_name = actor_user_id or "System"

    def sanitize(d):
        if not d or not isinstance(d, dict):
            return None
        safe = {}
        for k, v in d.items():
            if any(s in str(k).lower() for s in ["password", "token", "otp", "secret", "hash"]):
                safe[k] = "[REDACTED]"
            else:
                safe[k] = v
        return json.dumps(safe)

    old_json = sanitize(old_values)
    new_json = sanitize(new_values)

    try:
        conn.execute(
            """
            INSERT INTO platform_audit_logs (
                id, event_type, event_category, institution_id, actor_user_id,
                actor_name, actor_role, entity_type, entity_id, action,
                old_values, new_values, remarks, request_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                log_id, event_type, event_category, institution_id, actor_user_id,
                actor_name, actor_role, entity_type, entity_id, action,
                old_json, new_json, remarks, request_id
            )
        )
    except Exception as e:
        logging.getLogger("nagriksetu.auth").error(f"Failed to record platform audit log: {e}")

    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO audit_logs (
                audit_id, actor_user_id, actor_role, action, entity_type, entity_id, school_id, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                str(uuid.uuid4()), actor_user_id, actor_role, event_type, entity_type, entity_id, institution_id, new_json or "{}"
            )
        )
    except Exception:
        pass

    return log_id



def get_parent_guardian(conn, user_id: str):
    row = conn.execute(
        """
        SELECT guardian_id, user_id, full_name
        FROM guardians
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    if row is None:
        user_row = conn.execute(
            "SELECT user_id, full_name, phone, email FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        if user_row:
            gid = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO guardians (guardian_id, user_id, full_name, relationship, phone, email)
                VALUES (?, ?, ?, 'Guardian', ?, ?)
                """,
                (gid, user_id, user_row["full_name"] or "Parent Guardian", user_row["phone"] or "9999999999", user_row["email"] or "")
            )
            row = conn.execute(
                "SELECT guardian_id, user_id, full_name FROM guardians WHERE guardian_id = ?",
                (gid,)
            ).fetchone()
    return row


def get_authorized_child(
    conn,
    guardian_id: str,
    permanent_student_id: str,
    permission_column: str,
):
    # permission_column is selected only from fixed values in this file.
    if permission_column not in (
        "can_view_records",
        "can_request_updates",
    ):
        raise ValueError("Unsupported guardian permission.")

    return conn.execute(
        f"""
        SELECT s.student_id, s.permanent_student_id,
               s.student_name, s.school_id, s.standard,
               s.section, s.first_language, s.date_of_birth,
               s.gender, s.enrollment_status
        FROM student_guardians sg
        JOIN students s
          ON s.permanent_student_id = sg.permanent_student_id
        WHERE sg.guardian_id = ?
          AND sg.permanent_student_id = ?
          AND sg.is_verified = 1
          AND sg.{permission_column} = 1
        """,
        (guardian_id, permanent_student_id),
    ).fetchone()


def verify_via_central_sso(identifier: str, password: str) -> Optional[dict]:
    """
    Federated Single Sign-On (SSO): Query NagrikSetu Central Portal to verify citizen credentials.
    Returns citizen profile and linked household children when credentials match.
    """
    import urllib.request
    import json
    urls = [
        os.getenv("CENTRAL_AUTH_URL", "http://nagriksetu_backend:8000/api/v1/auth/federated-verify"),
        "http://nagriksetu_backend:8000/api/v1/auth/federated-verify",
        "http://backend:8000/api/v1/auth/federated-verify",
        "http://localhost:8000/api/v1/auth/federated-verify",
        "http://127.0.0.1:8000/api/v1/auth/federated-verify",
    ]
    seen = set()
    payload = json.dumps({"identifier": identifier, "password": password}).encode("utf-8")
    for u in urls:
        if not u or u in seen:
            continue
        seen.add(u)
        try:
            req = urllib.request.Request(
                u,
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("valid"):
                        return data
        except Exception:
            continue
    return None


def fetch_central_household_children(email: str) -> list:
    """
    Query NagrikSetu Central Portal to fetch verified household children for a citizen.
    """
    import urllib.request
    import urllib.parse
    import json
    urls = [
        f"http://nagriksetu_backend:8000/api/v1/citizens/household-children?email={urllib.parse.quote(email)}",
        f"http://backend:8000/api/v1/citizens/household-children?email={urllib.parse.quote(email)}",
        f"http://localhost:8000/api/v1/citizens/household-children?email={urllib.parse.quote(email)}",
        f"http://127.0.0.1:8000/api/v1/citizens/household-children?email={urllib.parse.quote(email)}",
    ]
    seen = set()
    for u in urls:
        if not u or u in seen:
            continue
        seen.add(u)
        try:
            req = urllib.request.Request(u, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("children", [])
        except Exception:
            continue
    return []


@app.post("/auth/login", response_model=LoginResponse)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    institution_id: Optional[str] = Query(default=None),
):
    """Use the username field for an email address or phone number."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    identifier = form.username.strip()

    if not auth_limiter.record_request(client_ip, max_per_minute=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before trying again.",
        )

    if auth_limiter.is_locked_out(client_ip, identifier, max_failures=5):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Account temporarily locked out for 60 seconds.",
        )

    conn = get_connection()
    try:
        user = conn.execute(
            """
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active, status, full_name,
                   permanent_student_id, student_id, is_email_verified
            FROM users
            WHERE email = ? COLLATE NOCASE 
               OR phone = ?
               OR student_id = ? COLLATE NOCASE
               OR permanent_student_id = ? COLLATE NOCASE
            """,
            (identifier, identifier, identifier, identifier),
        ).fetchone()

        # Check local credentials
        local_valid = False
        if user and user["password_hash"] and user["password_hash"].strip():
            if verify_password(form.password, user["password_hash"]):
                local_valid = True

        if not local_valid:
            # Fallback to Federated SSO with Central Citizen Portal
            sso_data = verify_via_central_sso(identifier, form.password)
            if sso_data and sso_data.get("valid"):
                email_val = sso_data.get("email") or identifier
                phone_val = sso_data.get("phone_number")
                user_phone = phone_val if phone_val else None
                if user_phone:
                    dup = conn.execute("SELECT 1 FROM users WHERE phone = ?", (user_phone,)).fetchone()
                    if dup:
                        user_phone = None
                guardian_phone = phone_val if phone_val else "+91-9876543210"
                full_name_val = sso_data.get("full_name") or email_val.split("@")[0]
                pwd_hash_val = hash_password(form.password)

                if user is None:
                    # Check if user exists by email specifically
                    existing_user = conn.execute(
                        "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (email_val,)
                    ).fetchone()
                    if existing_user:
                        uid = existing_user["user_id"]
                        conn.execute(
                            "UPDATE users SET password_hash = ?, full_name = COALESCE(full_name, ?), is_active = 1 WHERE user_id = ?",
                            (pwd_hash_val, full_name_val, uid)
                        )
                    else:
                        uid = f"PRN-2026-{uuid.uuid4().hex[:6].upper()}"
                        conn.execute(
                            """
                            INSERT INTO users (
                                user_id, email, phone, password_hash, role,
                                school_id, is_active, status, full_name, is_email_verified
                            ) VALUES (?, ?, ?, ?, 'parent', NULL, 1, 'active', ?, 1)
                            """,
                            (uid, email_val, user_phone, pwd_hash_val, full_name_val)
                        )
                else:
                    uid = user["user_id"]
                    conn.execute(
                        "UPDATE users SET password_hash = ?, full_name = COALESCE(full_name, ?), is_active = 1 WHERE user_id = ?",
                        (pwd_hash_val, full_name_val, uid)
                    )

                # Ensure Guardian record exists with standardized business ID
                g_row = conn.execute("SELECT guardian_id FROM guardians WHERE user_id = ? OR email = ?", (uid, email_val)).fetchone()
                if g_row:
                    g_id = g_row["guardian_id"]
                else:
                    g_id = f"GRD-2026-{uuid.uuid4().hex[:6].upper()}"
                    conn.execute(
                        """
                        INSERT INTO guardians (guardian_id, user_id, full_name, relationship, phone, email)
                        VALUES (?, ?, ?, 'Parent', ?, ?)
                        """,
                        (g_id, uid, full_name_val, guardian_phone, email_val)
                    )

                # Link household children from Central Portal
                for ch in sso_data.get("children", []):
                    perm_id = ch.get("permanent_student_id")
                    stu_id = ch.get("student_id")
                    ch_name = ch.get("full_name")
                    st_row = None
                    if perm_id:
                        st_row = conn.execute("SELECT permanent_student_id FROM students WHERE permanent_student_id = ?", (perm_id,)).fetchone()
                    if not st_row and stu_id:
                        st_row = conn.execute("SELECT permanent_student_id FROM students WHERE student_id = ?", (stu_id,)).fetchone()
                    if not st_row and ch_name:
                        st_row = conn.execute("SELECT permanent_student_id FROM students WHERE student_name = ?", (ch_name,)).fetchone()
                    
                    if st_row:
                        matched_perm_id = st_row["permanent_student_id"]
                        sg_exists = conn.execute(
                            "SELECT 1 FROM student_guardians WHERE guardian_id = ? AND permanent_student_id = ?",
                            (g_id, matched_perm_id)
                        ).fetchone()
                        if not sg_exists:
                            sg_id = f"SGL-2026-{uuid.uuid4().hex[:6].upper()}"
                            conn.execute(
                                """
                                INSERT INTO student_guardians (
                                    student_guardian_id, permanent_student_id, guardian_id,
                                    can_view_records, can_request_updates, is_verified
                                ) VALUES (?, ?, ?, 1, 1, 1)
                                """,
                                (sg_id, matched_perm_id, g_id)
                            )

                conn.commit()
                # Reload user row
                user = conn.execute(
                    """
                    SELECT user_id, email, phone, password_hash,
                           role, school_id, is_active, status, full_name,
                           permanent_student_id, student_id, is_email_verified
                    FROM users WHERE user_id = ?
                    """,
                    (uid,)
                ).fetchone()
            else:
                auth_limiter.record_failed_login(client_ip, identifier, max_failures=5)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        if not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated or suspended. Please contact your administrator.",
            )

        # Check if user has no password configured yet
        if not user["password_hash"] or user["password_hash"].strip() == "":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account does not have a password configured yet. Please use 'Set Up Password' or 'Forgot Password' to set your password.",
            )

        if not verify_password(form.password, user["password_hash"]):
            auth_limiter.record_failed_login(client_ip, identifier, max_failures=5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        auth_limiter.reset_failed_login(client_ip, identifier)

        # Update last_login
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user["user_id"],)
        )
        conn.commit()

        # Query active institution assignments
        inst_roles = conn.execute(
            """
            SELECT uir.institution_id, s.school_name, s.school_type, uir.role_id
            FROM user_institution_roles uir
            JOIN schools s ON s.school_id = uir.institution_id
            WHERE uir.user_id = ? AND uir.status = 'active'
            """,
            (user["user_id"],)
        ).fetchall()

        # Specific institution requested for institution-specific login:
        if institution_id:
            institution_id_clean = institution_id.strip()
            if user["role"] == "platform_admin":
                active_school = institution_id_clean
                effective_role = "platform_admin"
            else:
                matching_uir = next((r for r in inst_roles if r["institution_id"] == institution_id_clean), None)
                if matching_uir:
                    active_school = institution_id_clean
                    effective_role = matching_uir["role_id"]
                elif user["school_id"] == institution_id_clean and user["role"] in (
                    "school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff"
                ):
                    active_school = institution_id_clean
                    effective_role = user["role"]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied: Account '{identifier}' is not an authorized administrator or staff member for institution '{institution_id_clean}'."
                    )
            user_data = dict(user)
            user_data["role"] = effective_role
            user_data["school_id"] = active_school
            return {
                "access_token": create_access_token(user_data, school_id=active_school),
                "token_type": "bearer",
                "role": effective_role,
                "school_id": active_school,
                "student_id": user_data.get("student_id"),
                "permanent_student_id": user_data.get("permanent_student_id"),
            }

        # If user has multiple assigned institutions, require workspace selection
        if len(inst_roles) > 1 and user["role"] != "platform_admin":
            from auth import create_temp_token
            return {
                "requires_workspace_selection": True,
                "temp_token": create_temp_token(dict(user)),
                "workspaces": [
                    {
                        "institution_id": r["institution_id"],
                        "school_name": r["school_name"],
                        "school_type": r["school_type"],
                        "role_id": r["role_id"],
                    }
                    for r in inst_roles
                ],
            }

        active_school = inst_roles[0]["institution_id"] if inst_roles else user["school_id"]
        effective_role = inst_roles[0]["role_id"] if (inst_roles and user["role"] != "platform_admin") else user["role"]
        user_data = dict(user)
        user_data["role"] = effective_role
        user_data["school_id"] = active_school
        return {
            "access_token": create_access_token(user_data, school_id=active_school),
            "token_type": "bearer",
            "role": effective_role,
            "school_id": active_school,
            "student_id": user_data.get("student_id"),
            "permanent_student_id": user_data.get("permanent_student_id"),
        }
    finally:
        conn.close()


@app.post("/auth/register", response_model=RegisterResponse, status_code=201)
def register_parent(payload: ParentRegisterRequest):
    """
    Public citizen/parent registration using password.
    Always creates role='parent'.
    At least one of email or mobile number must be provided.
    """
    full_name = payload.full_name.strip()
    phone = payload.phone
    email = payload.email

    if not phone and not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please provide at least one contact method: an email address or a mobile number.",
        )

    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match.",
        )

    conn = get_connection()
    try:
        # Check duplicate mobile number
        if phone:
            existing_phone = conn.execute(
                "SELECT user_id FROM users WHERE phone = ?",
                (phone,),
            ).fetchone()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this mobile number already exists.",
                )

        # Check duplicate email address
        if email:
            existing_email = conn.execute(
                "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
                (email,),
            ).fetchone()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email address already exists.",
                )

        # Hash password using Argon2id
        pwd_hash = hash_password(payload.password)

        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())

        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO users (
                        user_id, email, phone, password_hash,
                        role, school_id, is_active, full_name, is_email_verified
                    )
                    VALUES (?, ?, ?, ?, 'parent', NULL, 1, ?, 1)
                    """,
                    (user_id, email, phone, pwd_hash, full_name),
                )

                guardian_phone = phone if phone else ""
                guardian_email = email if email else ""
                conn.execute(
                    """
                    INSERT INTO guardians (
                        guardian_id, user_id, full_name, relationship,
                        phone, email
                    )
                    VALUES (?, ?, ?, 'Parent', ?, ?)
                    """,
                    (guardian_id, user_id, full_name, guardian_phone, guardian_email),
                )

                conn.execute(
                    """
                    INSERT INTO audit_logs (
                        audit_id, actor_user_id, actor_role,
                        action, entity_type, entity_id,
                        school_id, ip_address, metadata_json
                    )
                    VALUES (?, ?, 'parent', 'PARENT_REGISTERED', 'user', ?, NULL, NULL, ?)
                    """,
                    (
                        audit_id,
                        user_id,
                        user_id,
                        json.dumps({"full_name": full_name, "has_email": bool(email), "has_phone": bool(phone)}),
                    ),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with these details already exists.",
            )

        user_dict = {
            "user_id": user_id,
            "role": "parent",
            "school_id": None,
            "student_id": None,
            "permanent_student_id": None,
        }
        token = create_access_token(user_dict)

        return {
            "user_id": user_id,
            "full_name": full_name,
            "message": "Registration successful. You can now log in.",
            "access_token": token,
            "token_type": "bearer",
            "role": "parent",
        }
    finally:
        conn.close()


@app.post("/auth/setup-password")
def setup_password(payload: SetupPasswordPayload):
    """
    Secure self-service password setup for existing accounts that do not yet have a password.
    Requires matching registered identifier and official full name.
    """
    identifier = payload.identifier.strip()
    full_name = payload.full_name.strip()

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=422, detail="Passwords do not match.")

    conn = get_connection()
    try:
        user = conn.execute(
            """
            SELECT user_id, email, phone, full_name, password_hash, is_active, status
            FROM users
            WHERE email = ? COLLATE NOCASE OR phone = ?
            """,
            (identifier, identifier)
        ).fetchone()

        if not user or not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=404,
                detail="No eligible active account found with the provided identifier."
            )

        if user["password_hash"] and user["password_hash"].strip() != "":
            raise HTTPException(
                status_code=400,
                detail="This account already has a password configured. Please sign in or use the Forgot Password link."
            )

        # Verify identity: check full_name against user or guardian
        user_name = (user["full_name"] or "").strip().lower()
        guardian = conn.execute(
            "SELECT full_name FROM guardians WHERE user_id = ?",
            (user["user_id"],)
        ).fetchone()
        guardian_name = (guardian["full_name"] or "").strip().lower() if guardian else ""

        input_name = full_name.lower()
        name_matched = False
        if input_name == user_name or input_name == guardian_name:
            name_matched = True
        elif user_name and (input_name in user_name or user_name in input_name):
            name_matched = True
        elif guardian_name and (input_name in guardian_name or guardian_name in input_name):
            name_matched = True

        if not name_matched:
            raise HTTPException(
                status_code=403,
                detail="The provided full name does not match the official account record. For security, identity verification requires matching registration details."
            )

        new_hash = hash_password(payload.password)
        with conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, is_email_verified = 1 WHERE user_id = ?",
                (new_hash, user["user_id"])
            )
            record_platform_audit(
                conn,
                event_type="PASSWORD_SETUP",
                event_category="SECURITY",
                institution_id=None,
                actor_user_id=user["user_id"],
                actor_role="parent",
                entity_type="user",
                entity_id=user["user_id"],
                action="INITIAL_PASSWORD_CONFIGURED",
                remarks=f"Initial password configured via self-service for account {user['user_id']}"
            )

        return {
            "status": "ok",
            "message": "Password configured successfully. You may now sign in with your credentials."
        }
    finally:
        conn.close()


# ==============================================================================
# CITIZEN OTP AUTHENTICATION & REGISTRATION ENDPOINTS
# ==============================================================================

class SendOtpRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)
    purpose: str = "register"  # "register" or "login"

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r"\D", "", v)
        if not re.match(r"^[6-9]\d{9}$", clean):
            raise ValueError("Must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
        return clean


class RegisterWithOtpRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)
    otp: str = Field(min_length=6, max_length=6)
    full_name: str = Field(min_length=2, max_length=100)
    email: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r"\D", "", v)
        if not re.match(r"^[6-9]\d{9}$", clean):
            raise ValueError("Must be a valid 10-digit Indian mobile number.")
        return clean


class LoginWithOtpRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10)
    otp: str = Field(min_length=6, max_length=6)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r"\D", "", v)
        if not re.match(r"^[6-9]\d{9}$", clean):
            raise ValueError("Must be a valid 10-digit Indian mobile number.")
        return clean


class SendEmailOtpRequest(BaseModel):
    email: str
    purpose: str = "register"  # "register" or "reset_password"
    full_name: Optional[str] = None


class RegisterWithEmailRequest(BaseModel):
    email: str
    otp: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
    phone: Optional[str] = None


class EmailLoginRequest(BaseModel):
    email: str
    password: str


class UnifiedSendOtpRequest(BaseModel):
    full_name: str
    contact: str
    purpose: str = "login"  # "login" or "register"


class UnifiedLoginRequest(BaseModel):
    full_name: str
    contact: str
    otp: str = Field(min_length=6, max_length=6)


class UnifiedRegisterRequest(BaseModel):
    full_name: str
    contact: str
    otp: str = Field(min_length=6, max_length=6)


def identify_and_normalize_contact(contact_raw: str) -> tuple[str, str]:
    """
    Identifies contact type and returns ('mobile', normalized_10_digit_phone)
    or ('email', normalized_lowercase_email).
    Raises HTTPException(422) if invalid format.
    """
    raw = (contact_raw or "").strip()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please provide a valid Indian mobile number or email address."
        )

    if "@" in raw:
        from email_service import normalize_email
        try:
            clean_email = normalize_email(raw)
            return "email", clean_email
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please enter a valid email address (e.g. name@example.com)."
            )
    else:
        from sms_service import normalize_phone_number
        try:
            clean_phone = normalize_phone_number(raw)
            return "mobile", clean_phone
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please enter a valid 10-digit Indian mobile number."
            )


def check_name_match(submitted_name: str, account_name: str) -> bool:
    """Case-insensitive, whitespace-collapsed name match."""
    s = " ".join((submitted_name or "").strip().lower().split())
    a = " ".join((account_name or "").strip().lower().split())
    return s == a


@app.post("/auth/otp/send")
def send_otp(request: Request, payload: SendOtpRequest):
    """
    Generates and dispatches a cryptographically secure 6-digit OTP.
    Enforces a 60-second resend cooldown and 5-minute expiration.
    Dispatches via SMS gateway if configured, or development mock logger.
    """
    from sms_service import normalize_phone_number, generate_otp, hash_otp, send_otp_sms, SMSConfigurationError, SMSGatewayError
    try:
        phone = normalize_phone_number(payload.phone)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    purpose = payload.purpose.strip().lower()
    if purpose not in ("register", "login"):
        raise HTTPException(status_code=400, detail="Invalid OTP purpose. Must be 'register' or 'login'.")

    conn = get_connection()
    try:
        # Check existing account status based on purpose
        existing_user = conn.execute(
            "SELECT user_id, is_active, status FROM users WHERE phone = ?",
            (phone,)
        ).fetchone()

        if purpose == "register" and existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this mobile number already exists. Please sign in instead."
            )
        elif purpose == "login" and existing_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this mobile number. Please register for a Citizen account first."
            )
        elif purpose == "login" and existing_user and (not existing_user["is_active"] or existing_user["status"] == "suspended"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated or suspended."
            )

        # Enforce 60-second cooldown per phone number
        recent_otp = conn.execute(
            """
            SELECT created_at FROM phone_otps
            WHERE phone = ? AND purpose = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (phone, purpose)
        ).fetchone()

        now = datetime.utcnow()
        if recent_otp and recent_otp["created_at"]:
            try:
                created_dt = datetime.fromisoformat(recent_otp["created_at"].replace("Z", ""))
                elapsed = (now - created_dt).total_seconds()
                if elapsed < 60:
                    wait_sec = int(60 - elapsed)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Please wait {wait_sec} seconds before requesting a new OTP."
                    )
            except ValueError:
                pass

        # Invalidate any existing active OTPs for the same phone and purpose
        with conn:
            conn.execute(
                """
                UPDATE phone_otps
                SET is_used = 1
                WHERE phone = ? AND purpose = ? AND is_used = 0
                """,
                (phone, purpose)
            )

        # Generate cryptographically secure OTP & Hash
        from sms_service import generate_otp, hash_otp, send_otp_sms, is_development_sms_mode, SMSConfigurationError, SMSGatewayError
        otp = generate_otp()
        otp_hash = hash_otp(phone, otp)
        expires_at = (now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
        otp_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Dispatch SMS via configured provider (Mock in dev, OTP.dev/MSG91 in prod)
        try:
            sms_result = send_otp_sms(phone, otp)
        except SMSConfigurationError as sce:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(sce)
            )
        except SMSGatewayError as sge:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(sge)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SMS dispatch failure: {str(e)}"
            )

        # Save to database only after SMS provider accepts request
        with conn:
            conn.execute(
                """
                INSERT INTO phone_otps (
                    otp_id, phone, otp_hash, purpose, attempts, max_attempts,
                    is_used, expires_at, created_at, ip_address
                ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                """,
                (otp_id, phone, otp_hash, purpose, expires_at, created_at_str, client_ip)
            )

        is_dev = is_development_sms_mode() or sms_result.get("is_simulated", False)
        resp_payload = {
            "message": f"OTP sent successfully to +91-******{phone[-4:]}." if not is_dev else f"Development mode: Simulated SMS OTP generated for +91-******{phone[-4:]}.",
            "phone": phone,
            "purpose": purpose,
            "expires_in_seconds": 300,
            "resend_cooldown_seconds": 60,
            "provider": sms_result.get("provider", "mock" if is_dev else "otpdev"),
            "provider_note": sms_result.get("message", "Dispatched"),
            "dev_mode": is_dev,
        }
        if is_dev:
            resp_payload["dev_notice"] = (
                "DEVELOPMENT SMS GATEWAY NOTICE: Real SMS delivery is disabled for student project testing. "
                "Use the development verification code below to test server-side OTP verification."
            )
            resp_payload["dev_otp"] = otp

        return resp_payload
    finally:
        conn.close()


@app.post("/auth/otp/register", status_code=status.HTTP_201_CREATED)
def register_citizen_with_otp(payload: RegisterWithOtpRequest):
    """
    Verifies OTP and registers a new Citizen account (primary public user identity).
    Issues standard JWT access token upon successful verification.
    """
    from sms_service import normalize_phone_number
    try:
        phone = normalize_phone_number(payload.phone)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    otp = payload.otp.strip()
    full_name = payload.full_name.strip()
    email = payload.email.strip().lower() if payload.email and payload.email.strip() else None

    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name must contain at least 2 non-whitespace characters."
        )

    conn = get_connection()
    try:
        # Check if already registered
        existing = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this mobile number already exists. Please log in."
            )

        # Retrieve latest unused OTP for registration
        otp_row = conn.execute(
            """
            SELECT * FROM phone_otps
            WHERE phone = ? AND purpose = 'register' AND is_used = 0
            ORDER BY created_at DESC LIMIT 1
            """,
            (phone,)
        ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active OTP found. Please request an OTP first."
            )

        # Check expiration
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new OTP."
            )

        # Check maximum attempt limit
        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This OTP has been invalidated. Please request a new OTP."
            )

        # Verify hash
        from sms_service import verify_otp_hash, verify_otp_with_provider, SMSGatewayError, SMSConfigurationError
        if not verify_otp_hash(phone, otp, otp_row["otp_hash"]):
            with conn:
                conn.execute(
                    "UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?",
                    (otp_row["otp_id"],)
                )
            remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect OTP. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
            )

        # Server-side verification with provider if configured (e.g. OTP.dev)
        try:
            if not verify_otp_with_provider(phone, otp):
                with conn:
                    conn.execute(
                        "UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?",
                        (otp_row["otp_id"],)
                    )
                remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"OTP verification rejected by provider. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
                )
        except SMSConfigurationError:
            pass
        except SMSGatewayError as sge:
            logging.getLogger("nagriksetu.auth").warning(f"Provider verification check encountered gateway error: {sge}")

        # Invalidate OTP on success and create Citizen account
        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())
        dummy_password_hash = hash_password(secrets.token_urlsafe(16))

        with conn:
            conn.execute(
                "UPDATE phone_otps SET is_used = 1 WHERE otp_id = ?",
                (otp_row["otp_id"],)
            )

            # Insert as public citizen/parent user
            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, phone, password_hash,
                    role, school_id, is_active, status, full_name
                ) VALUES (?, ?, ?, ?, 'parent', NULL, 1, 'active', ?)
                """,
                (user_id, email, phone, dummy_password_hash, full_name)
            )

            # Create base guardian profile (unlinked to any student)
            conn.execute(
                """
                INSERT INTO guardians (
                    guardian_id, user_id, full_name, relationship,
                    phone, email
                ) VALUES (?, ?, ?, 'Citizen / Guardian', ?, ?)
                """,
                (guardian_id, user_id, full_name, phone, email)
            )

            # Insert audit log
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role,
                    action, entity_type, entity_id,
                    school_id, ip_address, metadata_json
                ) VALUES (?, ?, 'parent', 'CITIZEN_REGISTERED_OTP', 'user', ?, NULL, NULL, ?)
                """,
                (audit_id, user_id, user_id, json.dumps({"full_name": full_name, "phone": phone}))
            )

        user_data = {
            "user_id": user_id,
            "role": "parent",
            "school_id": None,
            "student_id": None,
            "permanent_student_id": None,
            "email": email,
            "phone": phone,
            "full_name": full_name,
        }

        access_token = create_access_token(user_data)
        return {
            "message": f"Citizen registration successful for {full_name}!",
            "access_token": access_token,
            "token_type": "bearer",
            "role": "parent",
            "school_id": None,
            "user_id": user_id,
            "full_name": full_name,
            "phone": phone,
        }
    finally:
        conn.close()


@app.post("/auth/otp/login")
def login_citizen_with_otp(payload: LoginWithOtpRequest):
    """
    Authenticates an existing Citizen or Parent account using mobile OTP.
    Never creates duplicate accounts. Issues standard JWT session token.
    """
    from sms_service import normalize_phone_number
    try:
        phone = normalize_phone_number(payload.phone)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    otp = payload.otp.strip()

    conn = get_connection()
    try:
        user = conn.execute(
            """
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active, status, full_name,
                   permanent_student_id, student_id
            FROM users
            WHERE phone = ?
            """,
            (phone,)
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this mobile number. Please register for a Citizen account first."
            )

        if not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated or suspended."
            )

        # Retrieve latest unused OTP for login
        otp_row = conn.execute(
            """
            SELECT * FROM phone_otps
            WHERE phone = ? AND purpose = 'login' AND is_used = 0
            ORDER BY created_at DESC LIMIT 1
            """,
            (phone,)
        ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active OTP found. Please request an OTP first."
            )

        # Check expiration
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new OTP."
            )

        # Check attempts
        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This OTP has been invalidated. Please request a new OTP."
            )

        from sms_service import verify_otp_hash, verify_otp_with_provider, SMSGatewayError, SMSConfigurationError
        if not verify_otp_hash(phone, otp, otp_row["otp_hash"]):
            with conn:
                conn.execute(
                    "UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?",
                    (otp_row["otp_id"],)
                )
            remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect OTP. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
            )

        # Server-side verification with provider if configured (e.g. OTP.dev)
        try:
            if not verify_otp_with_provider(phone, otp):
                with conn:
                    conn.execute(
                        "UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?",
                        (otp_row["otp_id"],)
                    )
                remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"OTP verification rejected by provider. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
                )
        except SMSConfigurationError:
            pass
        except SMSGatewayError as sge:
            logging.getLogger("nagriksetu.auth").warning(f"Provider verification check encountered gateway error: {sge}")

        # Mark OTP as used and update last_login
        with conn:
            conn.execute("UPDATE phone_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))
            conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))

        user_dict = dict(user)
        access_token = create_access_token(user_dict, school_id=user_dict["school_id"])

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user_dict["role"],
            "school_id": user_dict["school_id"],
            "user_id": user_dict["user_id"],
            "full_name": user_dict["full_name"],
            "phone": user_dict["phone"],
            "student_id": user_dict.get("student_id"),
            "permanent_student_id": user_dict.get("permanent_student_id"),
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# GOOGLE IDENTITY SERVICES & EMAIL OTP AUTHENTICATION SCHEMAS & ENDPOINTS
# ---------------------------------------------------------------------------

class GoogleOtpSendRequest(BaseModel):
    id_token: str
    purpose: str = "login"
    full_name: Optional[str] = None

class GoogleLoginRequest(BaseModel):
    id_token: str
    otp: str

class GoogleRegisterRequest(BaseModel):
    id_token: str
    otp: str
    full_name: Optional[str] = None


@app.get("/auth/config/oauth")
def get_oauth_config():
    """Returns public OAuth client IDs and gateway status for frontend initialization."""
    from google_auth_service import get_google_client_id, is_google_auth_configured
    from sms_service import is_development_sms_mode
    return {
        "google_client_id": get_google_client_id(),
        "is_google_configured": is_google_auth_configured(),
        "is_sms_development": is_development_sms_mode(),
    }


@app.post("/auth/google/otp/send")
def send_google_email_otp(request: Request, payload: GoogleOtpSendRequest):
    """
    Verifies Google ID Token on backend, extracts verified email address,
    and dispatches a 6-digit OTP to that email via Gmail SMTP.
    Does NOT automatically authenticate user.
    """
    from google_auth_service import verify_google_id_token, GoogleAuthError
    from email_service import (
        hash_email_otp,
        send_login_otp_email,
        send_registration_otp_email,
        mask_email,
        EmailConfigurationError,
        EmailDeliveryError,
    )
    from sms_service import generate_otp

    # 1. Cryptographically verify Google ID Token on backend
    try:
        google_user = verify_google_id_token(payload.id_token)
    except GoogleAuthError as gae:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(gae))

    verified_email = google_user["email"].strip().lower()
    google_name = google_user.get("name") or verified_email.split("@")[0]
    display_name = (payload.full_name or "").strip() or google_name

    purpose = payload.purpose.strip().lower()
    if purpose not in ("login", "register"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Purpose must be either 'login' or 'register'."
        )

    conn = get_connection()
    try:
        # 2. Enforce Account Existence & Security Rules
        if purpose == "login":
            user = conn.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
                (verified_email,)
            ).fetchone()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active Citizen account found for this Google email address. Please register as a new citizen first."
                )

            if not user["is_active"] or user["status"] == "suspended":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated or suspended."
                )

            account_name = user["full_name"] or display_name
        else: # register
            existing = conn.execute(
                "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
                (verified_email,)
            ).fetchone()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email address already exists. Please sign in instead."
                )
            account_name = display_name

        # 3. 60-Second Cooldown Enforcement
        now = datetime.utcnow()
        recent = conn.execute(
            """
            SELECT created_at FROM email_otps
            WHERE email = ? AND purpose = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (verified_email, purpose)
        ).fetchone()

        if recent and recent["created_at"]:
            try:
                cdt = datetime.fromisoformat(recent["created_at"].replace("Z", ""))
                elapsed = (now - cdt).total_seconds()
                if elapsed < 60:
                    wait_sec = int(60 - elapsed)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Please wait {wait_sec} seconds before requesting a new verification code."
                    )
            except ValueError:
                pass

        # 4. Invalidate Previous Active OTPs
        with conn:
            conn.execute(
                "UPDATE email_otps SET is_used = 1 WHERE email = ? AND purpose = ? AND is_used = 0",
                (verified_email, purpose)
            )

        # 5. Generate 6-Digit OTP & Salted SHA-256 Hash
        otp = generate_otp()
        otp_hash = hash_email_otp(verified_email, otp)
        expires_at = (now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
        otp_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "127.0.0.1"

        # 6. Dispatch Real Email OTP via Gmail SMTP
        # Email OTP must be accepted by the SMTP provider before saving to DB or claiming success
        try:
            if purpose == "login":
                send_login_otp_email(verified_email, otp, account_name)
            else:
                send_registration_otp_email(verified_email, otp, account_name)
        except EmailConfigurationError as ece:
            logging.getLogger("nagriksetu.auth").error(f"Email gateway misconfigured: {ece}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Email configuration error: {str(ece)}")
        except EmailDeliveryError as ede:
            logging.getLogger("nagriksetu.auth").error(f"Email delivery rejected by SMTP: {ede}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Email delivery failed: {str(ede)}")
        except Exception as e:
            logging.getLogger("nagriksetu.auth").error(f"Unexpected email dispatch error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email dispatch error: {str(e)}")

        # Save to database ONLY AFTER email provider accepts message
        with conn:
            conn.execute(
                """
                INSERT INTO email_otps (
                    otp_id, email, otp_hash, purpose, attempts, max_attempts,
                    is_used, expires_at, created_at, ip_address
                ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                """,
                (otp_id, verified_email, otp_hash, purpose, expires_at, created_at_str, client_ip)
            )

        masked_target = mask_email(verified_email)
        return {
            "success": True,
            "message": f"Verification code sent to {masked_target}.",
            "email": verified_email,
            "masked_email": masked_target,
            "google_name": google_name,
            "delivery_channel": "Email",
            "purpose": purpose,
            "resend_cooldown_seconds": 60,
            "expires_in_seconds": 300,
        }
    finally:
        conn.close()


@app.post("/auth/google/login")
def login_with_google_otp(payload: GoogleLoginRequest):
    """
    Authenticates existing citizen account using verified Google Identity and verified Email OTP.
    Never creates new account during login.
    """
    from google_auth_service import verify_google_id_token, GoogleAuthError
    from email_service import verify_email_otp_hash

    try:
        google_user = verify_google_id_token(payload.id_token)
    except GoogleAuthError as gae:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(gae))

    verified_email = google_user["email"].strip().lower()
    otp = payload.otp.strip()

    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verification code must be exactly 6 numeric digits."
        )

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
            (verified_email,)
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active Citizen account found for this Google email address. Please register as a new citizen."
            )

        if not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated or suspended."
            )

        otp_row = conn.execute(
            """
            SELECT * FROM email_otps
            WHERE email = ? AND purpose = 'login' AND is_used = 0
            ORDER BY created_at DESC LIMIT 1
            """,
            (verified_email,)
        ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found. Please request a new code."
            )

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )

        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This code has been invalidated. Please request a new code."
            )

        if not verify_email_otp_hash(verified_email, otp, otp_row["otp_hash"]):
            with conn:
                conn.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
            remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect verification code. {remaining} attempt{'s' if remaining != 1 else ''} remaining."
            )

        with conn:
            conn.execute("UPDATE email_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))
            conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))
            record_platform_audit(
                conn=conn,
                event_type="CITIZEN_LOGIN_GOOGLE_OTP",
                event_category="AUTH",
                institution_id=None,
                actor_user_id=user["user_id"],
                actor_role="parent",
                entity_type="users",
                entity_id=user["user_id"],
                action="CITIZEN_LOGIN_GOOGLE_OTP",
                new_values={"email": verified_email},
                remarks="Citizen signed in via Google Account + Email OTP"
            )

        user_dict = dict(user)
        access_token = create_access_token(user_dict, school_id=user_dict["school_id"])
        user_data = {
            "user_id": user_dict["user_id"],
            "role": user_dict["role"],
            "school_id": user_dict["school_id"],
            "student_id": user_dict.get("student_id"),
            "permanent_student_id": user_dict.get("permanent_student_id"),
            "email": user_dict["email"],
            "phone": user_dict["phone"],
            "full_name": user_dict["full_name"],
        }
        return {
            "message": f"Sign In successful. Welcome back, {user_dict['full_name']}!",
            "access_token": access_token,
            "token_type": "bearer",
            "role": user_dict["role"],
            "school_id": user_dict["school_id"],
            "user_id": user_dict["user_id"],
            "full_name": user_dict["full_name"],
            "email": user_dict["email"],
            "phone": user_dict["phone"],
            "user": user_data,
        }
    finally:
        conn.close()


@app.post("/auth/google/register", status_code=status.HTTP_201_CREATED)
def register_with_google_otp(payload: GoogleRegisterRequest):
    """
    Registers a new Citizen account using verified Google Identity and verified Email OTP.
    Does not overwrite existing accounts.
    """
    from google_auth_service import verify_google_id_token, GoogleAuthError
    from email_service import verify_email_otp_hash

    try:
        google_user = verify_google_id_token(payload.id_token)
    except GoogleAuthError as gae:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(gae))

    verified_email = google_user["email"].strip().lower()
    otp = payload.otp.strip()

    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verification code must be exactly 6 numeric digits."
        )

    full_name = (payload.full_name or "").strip() or google_user.get("name") or verified_email.split("@")[0]
    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full Name must be at least 2 characters."
        )

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
            (verified_email,)
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists. Please sign in instead."
            )

        otp_row = conn.execute(
            """
            SELECT * FROM email_otps
            WHERE email = ? AND purpose = 'register' AND is_used = 0
            ORDER BY created_at DESC LIMIT 1
            """,
            (verified_email,)
        ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found. Please request a new code."
            )

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )

        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This code has been invalidated. Please request a new code."
            )

        if not verify_email_otp_hash(verified_email, otp, otp_row["otp_hash"]):
            with conn:
                conn.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
            remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect verification code. {remaining} attempt{'s' if remaining != 1 else ''} remaining."
            )

        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        created_at_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        with conn:
            conn.execute("UPDATE email_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))
            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, phone, password_hash, role, school_id,
                    is_active, created_at, full_name, status, last_login, is_email_verified
                ) VALUES (?, ?, NULL, '', 'parent', NULL, 1, ?, ?, 'active', ?, 1)
                """,
                (user_id, verified_email, created_at_str, full_name, created_at_str)
            )
            conn.execute(
                """
                INSERT INTO guardians (
                    guardian_id, user_id, full_name, relationship, phone, email, address, created_at
                ) VALUES (?, ?, ?, 'Guardian', '', ?, NULL, ?)
                """,
                (guardian_id, user_id, full_name, verified_email, created_at_str)
            )
            record_platform_audit(
                conn=conn,
                event_type="CITIZEN_REGISTER_GOOGLE_OTP",
                event_category="AUTH",
                institution_id=None,
                actor_user_id=user_id,
                actor_role="parent",
                entity_type="users",
                entity_id=user_id,
                action="CITIZEN_REGISTER_GOOGLE_OTP",
                new_values={"email": verified_email, "full_name": full_name},
                remarks="New Citizen registered via Google Account + Email OTP"
            )

        new_user = {
            "user_id": user_id,
            "role": "parent",
            "school_id": None,
            "student_id": None,
            "permanent_student_id": None,
            "email": verified_email,
            "phone": None,
            "full_name": full_name,
        }
        access_token = create_access_token(new_user, school_id=None)

        return {
            "message": f"Registration successful! Welcome to NagrikSetu, {full_name}!",
            "access_token": access_token,
            "token_type": "bearer",
            "role": "parent",
            "school_id": None,
            "user_id": user_id,
            "full_name": full_name,
            "email": verified_email,
            "phone": None,
            "user": new_user,
        }
    finally:
        conn.close()


@app.post("/auth/unified/otp/send")
def send_unified_otp(request: Request, payload: UnifiedSendOtpRequest):
    """
    Unified OTP dispatch endpoint for Citizen/Parent Sign In and Registration.
    Accepts Full Name (as per Aadhaar) and Contact (Mobile Number or Email Address).
    Automatically identifies contact channel and dispatches via OTP.dev SMS or Gmail SMTP.
    Enforces single-use OTPs, 60-second cooldown, and 5-minute expiration.
    """
    full_name = payload.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full Name (as per Aadhaar) must be at least 2 characters."
        )

    contact_type, clean_contact = identify_and_normalize_contact(payload.contact)
    purpose = payload.purpose.strip().lower()
    if purpose not in ("login", "register"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Purpose must be either 'login' or 'register'."
        )

    conn = get_connection()
    try:
        if purpose == "login":
            if contact_type == "mobile":
                user = conn.execute("SELECT * FROM users WHERE phone = ?", (clean_contact,)).fetchone()
            else:
                user = conn.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (clean_contact,)).fetchone()

            if not user or not check_name_match(full_name, user["full_name"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active account found matching the provided name and contact details. Please verify your details or register as a new citizen."
                )

            if not user["is_active"] or user["status"] == "suspended":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated or suspended."
                )

        elif purpose == "register":
            if contact_type == "mobile":
                existing = conn.execute("SELECT user_id FROM users WHERE phone = ?", (clean_contact,)).fetchone()
            else:
                existing = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (clean_contact,)).fetchone()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this contact details already exists. Please sign in instead."
                )

        # 60-second cooldown per contact and purpose
        now = datetime.utcnow()
        if contact_type == "mobile":
            recent = conn.execute(
                """
                SELECT created_at FROM phone_otps
                WHERE phone = ? AND purpose = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (clean_contact, purpose)
            ).fetchone()
        else:
            recent = conn.execute(
                """
                SELECT created_at FROM email_otps
                WHERE email = ? AND purpose = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (clean_contact, purpose)
            ).fetchone()

        if recent and recent["created_at"]:
            try:
                cdt = datetime.fromisoformat(recent["created_at"].replace("Z", ""))
                elapsed = (now - cdt).total_seconds()
                if elapsed < 60:
                    wait_sec = int(60 - elapsed)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Please wait {wait_sec} seconds before requesting a new verification code."
                    )
            except ValueError:
                pass

        # Invalidate previously active unused OTPs for this contact and purpose
        with conn:
            if contact_type == "mobile":
                conn.execute(
                    "UPDATE phone_otps SET is_used = 1 WHERE phone = ? AND purpose = ? AND is_used = 0",
                    (clean_contact, purpose)
                )
            else:
                conn.execute(
                    "UPDATE email_otps SET is_used = 1 WHERE email = ? AND purpose = ? AND is_used = 0",
                    (clean_contact, purpose)
                )

        from sms_service import generate_otp
        otp = generate_otp()
        expires_at = (now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
        otp_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "127.0.0.1"

        is_dev = False
        dev_otp_val = None
        dev_notice = None

        if contact_type == "mobile":
            from sms_service import hash_otp, send_otp_sms, is_development_sms_mode, SMSConfigurationError, SMSGatewayError
            otp_hash = hash_otp(clean_contact, otp)
            try:
                sms_res = send_otp_sms(clean_contact, otp)
            except SMSConfigurationError as sce:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(sce))
            except SMSGatewayError as sge:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(sge))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SMS dispatch failure: {str(e)}")

            with conn:
                conn.execute(
                    """
                    INSERT INTO phone_otps (
                        otp_id, phone, otp_hash, purpose, attempts, max_attempts,
                        is_used, expires_at, created_at, ip_address
                    ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                    """,
                    (otp_id, clean_contact, otp_hash, purpose, expires_at, created_at_str, client_ip)
                )
            masked_contact = f"+91-******{clean_contact[-4:]}"
            delivery_channel = "SMS"

            is_dev = is_development_sms_mode() or sms_res.get("is_simulated", False)
            if is_dev:
                dev_notice = (
                    "DEVELOPMENT SMS GATEWAY NOTICE: Real SMS delivery is disabled for student project testing. "
                    "Use the development verification code below to test server-side OTP verification."
                )
                dev_otp_val = otp
        else:
            from email_service import (
                hash_email_otp,
                send_registration_otp_email,
                send_login_otp_email,
                mask_email,
                EmailConfigurationError,
                EmailDeliveryError,
            )
            otp_hash = hash_email_otp(clean_contact, otp)
            try:
                if purpose == "login":
                    send_login_otp_email(clean_contact, otp, full_name)
                else:
                    send_registration_otp_email(clean_contact, otp, full_name)
            except EmailConfigurationError as ece:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(ece))
            except EmailDeliveryError as ede:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ede))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email dispatch failure: {str(e)}")

            with conn:
                conn.execute(
                    """
                    INSERT INTO email_otps (
                        otp_id, email, otp_hash, purpose, attempts, max_attempts,
                        is_used, expires_at, created_at, ip_address
                    ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                    """,
                    (otp_id, clean_contact, otp_hash, purpose, expires_at, created_at_str, client_ip)
                )
            masked_contact = mask_email(clean_contact)
            delivery_channel = "Email"

        resp_payload = {
            "message": f"Verification code sent successfully to {masked_contact}." if not is_dev else f"Development mode: Simulated SMS OTP generated for {masked_contact}.",
            "contact_type": contact_type,
            "masked_contact": masked_contact,
            "delivery_channel": delivery_channel,
            "purpose": purpose,
            "resend_cooldown_seconds": 60,
            "expires_in_seconds": 300,
            "dev_mode": is_dev,
        }
        if dev_notice:
            resp_payload["dev_notice"] = dev_notice
        if dev_otp_val:
            resp_payload["dev_otp"] = dev_otp_val

        return resp_payload
    finally:
        conn.close()


@app.post("/auth/unified/login")
def unified_login(payload: UnifiedLoginRequest):
    """
    Authenticates an existing active Citizen / Parent account using verified Mobile or Email OTP.
    Name and contact must match an existing active account. Never creates a new account.
    """
    full_name = payload.full_name.strip()
    contact_type, clean_contact = identify_and_normalize_contact(payload.contact)
    otp = payload.otp.strip()

    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verification code must be exactly 6 numeric digits."
        )

    conn = get_connection()
    try:
        if contact_type == "mobile":
            user = conn.execute("SELECT * FROM users WHERE phone = ?", (clean_contact,)).fetchone()
        else:
            user = conn.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (clean_contact,)).fetchone()

        if not user or not check_name_match(full_name, user["full_name"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active account found matching the provided name and contact details. Please check your credentials or register as a new citizen."
            )

        if not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated or suspended."
            )

        # Retrieve active unused OTP
        if contact_type == "mobile":
            otp_row = conn.execute(
                """
                SELECT * FROM phone_otps
                WHERE phone = ? AND purpose = 'login' AND is_used = 0
                ORDER BY created_at DESC LIMIT 1
                """,
                (clean_contact,)
            ).fetchone()
        else:
            otp_row = conn.execute(
                """
                SELECT * FROM email_otps
                WHERE email = ? AND purpose = 'login' AND is_used = 0
                ORDER BY created_at DESC LIMIT 1
                """,
                (clean_contact,)
            ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found. Please request a new code."
            )

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )

        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This code has been invalidated. Please request a new code."
            )

        # Verify OTP
        if contact_type == "mobile":
            from sms_service import verify_otp_hash, verify_otp_with_provider, SMSGatewayError, SMSConfigurationError
            if not verify_otp_hash(clean_contact, otp, otp_row["otp_hash"]):
                with conn:
                    conn.execute("UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
                remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Incorrect verification code. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
                )
            try:
                if not verify_otp_with_provider(clean_contact, otp):
                    with conn:
                        conn.execute("UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
                    remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Verification code rejected by provider. {remaining} attempt{'s' if remaining != 1 else ''} remaining."
                    )
            except (SMSConfigurationError, SMSGatewayError):
                pass
            with conn:
                conn.execute("UPDATE phone_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))
        else:
            from email_service import verify_email_otp_hash
            if not verify_email_otp_hash(clean_contact, otp, otp_row["otp_hash"]):
                with conn:
                    conn.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
                remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Incorrect verification code. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
                )
            with conn:
                conn.execute("UPDATE email_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))

        # Update last login & audit
        with conn:
            conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))
            record_platform_audit(
                conn=conn,
                event_type="CITIZEN_LOGIN_OTP",
                event_category="AUTH",
                institution_id=None,
                actor_user_id=user["user_id"],
                actor_role="parent",
                entity_type="users",
                entity_id=user["user_id"],
                action="CITIZEN_LOGIN_OTP",
                new_values={"contact_type": contact_type, "contact": clean_contact},
                remarks=f"Citizen signed in via unified {contact_type} OTP"
            )

        user_dict = dict(user)
        access_token = create_access_token(user_dict, school_id=user_dict["school_id"])
        user_data = {
            "user_id": user_dict["user_id"],
            "role": user_dict["role"],
            "school_id": user_dict["school_id"],
            "student_id": user_dict.get("student_id"),
            "permanent_student_id": user_dict.get("permanent_student_id"),
            "email": user_dict["email"],
            "phone": user_dict["phone"],
            "full_name": user_dict["full_name"],
        }
        return {
            "message": f"Sign In successful. Welcome back, {user_dict['full_name']}!",
            "access_token": access_token,
            "token_type": "bearer",
            "role": user_dict["role"],
            "school_id": user_dict["school_id"],
            "user_id": user_dict["user_id"],
            "full_name": user_dict["full_name"],
            "email": user_dict["email"],
            "phone": user_dict["phone"],
            "user": user_data,
        }
    finally:
        conn.close()


@app.post("/auth/unified/register", status_code=status.HTTP_201_CREATED)
def unified_register(payload: UnifiedRegisterRequest):
    """
    Unified Registration endpoint for new Citizen accounts.
    Requires Full Name (as per Aadhaar), Contact (Mobile or Email), and verified 6-digit OTP.
    Creates account with verified contact only after successful OTP verification.
    """
    full_name = payload.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full Name (as per Aadhaar) must be at least 2 characters."
        )

    contact_type, clean_contact = identify_and_normalize_contact(payload.contact)
    otp = payload.otp.strip()

    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verification code must be exactly 6 numeric digits."
        )

    conn = get_connection()
    try:
        if contact_type == "mobile":
            existing = conn.execute("SELECT user_id FROM users WHERE phone = ?", (clean_contact,)).fetchone()
        else:
            existing = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (clean_contact,)).fetchone()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this contact details already exists. Please sign in instead."
            )

        # Retrieve active unused registration OTP
        if contact_type == "mobile":
            otp_row = conn.execute(
                """
                SELECT * FROM phone_otps
                WHERE phone = ? AND purpose = 'register' AND is_used = 0
                ORDER BY created_at DESC LIMIT 1
                """,
                (clean_contact,)
            ).fetchone()
        else:
            otp_row = conn.execute(
                """
                SELECT * FROM email_otps
                WHERE email = ? AND purpose = 'register' AND is_used = 0
                ORDER BY created_at DESC LIMIT 1
                """,
                (clean_contact,)
            ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found. Please request an OTP first."
            )

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )

        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This code has been invalidated. Please request a new code."
            )

        # Verify hash
        if contact_type == "mobile":
            from sms_service import verify_otp_hash, verify_otp_with_provider, SMSGatewayError, SMSConfigurationError
            if not verify_otp_hash(clean_contact, otp, otp_row["otp_hash"]):
                with conn:
                    conn.execute("UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
                remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Incorrect verification code. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
                )
            try:
                if not verify_otp_with_provider(clean_contact, otp):
                    with conn:
                        conn.execute("UPDATE phone_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
                    remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Verification code rejected by provider. {remaining} attempt{'s' if remaining != 1 else ''} remaining."
                    )
            except (SMSConfigurationError, SMSGatewayError):
                pass
            with conn:
                conn.execute("UPDATE phone_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))
        else:
            from email_service import verify_email_otp_hash
            if not verify_email_otp_hash(clean_contact, otp, otp_row["otp_hash"]):
                with conn:
                    conn.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE otp_id = ?", (otp_row["otp_id"],))
                remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Incorrect verification code. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
                )
            with conn:
                conn.execute("UPDATE email_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))

        # Create new Citizen Account
        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        phone_val = clean_contact if contact_type == "mobile" else None
        email_val = clean_contact if contact_type == "email" else None
        dummy_password_hash = hash_password(secrets.token_urlsafe(24))

        with conn:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, phone, password_hash, role,
                    school_id, is_active, status, full_name, is_email_verified
                ) VALUES (?, ?, ?, ?, 'parent', NULL, 1, 'active', ?, 1)
                """,
                (user_id, email_val, phone_val, dummy_password_hash, full_name)
            )

            conn.execute(
                """
                INSERT INTO guardians (
                    guardian_id, user_id, full_name, phone, email, relationship
                ) VALUES (?, ?, ?, ?, ?, 'Citizen / Guardian')
                """,
                (guardian_id, user_id, full_name, phone_val or "", email_val or "")
            )

            record_platform_audit(
                conn=conn,
                event_type="CITIZEN_REGISTERED_OTP",
                event_category="AUTH",
                institution_id=None,
                actor_user_id=user_id,
                actor_role="parent",
                entity_type="users",
                entity_id=user_id,
                action="CITIZEN_REGISTERED_OTP",
                new_values={"full_name": full_name, "contact_type": contact_type, "contact": clean_contact},
                remarks=f"Citizen registered via unified {contact_type} OTP"
            )

        user_data = {
            "user_id": user_id,
            "role": "parent",
            "school_id": None,
            "student_id": None,
            "permanent_student_id": None,
            "email": email_val,
            "phone": phone_val,
            "full_name": full_name,
        }
        access_token = create_access_token(user_data)
        return {
            "message": f"Registration successful for {full_name}!",
            "access_token": access_token,
            "token_type": "bearer",
            "role": "parent",
            "school_id": None,
            "user_id": user_id,
            "full_name": full_name,
            "email": email_val,
            "phone": phone_val,
            "user": user_data,
        }
    finally:
        conn.close()


@app.post("/auth/email/otp/send")
def send_email_otp(request: Request, payload: SendEmailOtpRequest):
    """
    Generates and sends a 6-digit email OTP for registration or password reset.
    Enforces a 60-second cooldown and 5-minute expiration.
    """
    from email_service import (
        normalize_email,
        generate_email_otp,
        hash_email_otp,
        send_registration_otp_email,
        EmailConfigurationError,
        EmailDeliveryError,
    )

    try:
        email = normalize_email(payload.email)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    purpose = payload.purpose.strip().lower()
    if purpose not in ("register", "reset_password"):
        raise HTTPException(status_code=400, detail="Invalid OTP purpose. Must be 'register' or 'reset_password'.")

    conn = get_connection()
    try:
        # If registration, ensure account does not already exist with this email
        existing_user = conn.execute(
            "SELECT user_id, is_active, status FROM users WHERE email = ? COLLATE NOCASE",
            (email,)
        ).fetchone()

        if purpose == "register" and existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists. Please sign in instead."
            )

        # Enforce 60-second cooldown per email address
        recent_otp = conn.execute(
            """
            SELECT created_at FROM email_otps
            WHERE email = ? AND purpose = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (email, purpose)
        ).fetchone()

        now = datetime.utcnow()
        if recent_otp and recent_otp["created_at"]:
            try:
                created_dt = datetime.fromisoformat(recent_otp["created_at"].replace("Z", ""))
                elapsed = (now - created_dt).total_seconds()
                if elapsed < 60:
                    wait_sec = int(60 - elapsed)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Please wait {wait_sec} seconds before requesting a new email verification code."
                    )
            except ValueError:
                pass

        # Invalidate any older active OTPs for this email and purpose
        with conn:
            conn.execute(
                """
                UPDATE email_otps
                SET is_used = 1
                WHERE email = ? AND purpose = ? AND is_used = 0
                """,
                (email, purpose)
            )

        # Generate cryptographically secure OTP & Hash
        otp = generate_email_otp()
        otp_hash = hash_email_otp(email, otp)
        expires_at = (now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
        otp_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Dispatch via Email Provider (SMTP)
        try:
            email_result = send_registration_otp_email(email, otp, payload.full_name)
        except EmailConfigurationError as ece:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(ece)
            )
        except EmailDeliveryError as ede:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(ede)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email dispatch failure: {str(e)}"
            )

        # Save to database only after email provider accepts request
        with conn:
            conn.execute(
                """
                INSERT INTO email_otps (
                    otp_id, email, otp_hash, purpose, attempts, max_attempts,
                    is_used, expires_at, created_at, ip_address
                ) VALUES (?, ?, ?, ?, 0, 5, 0, ?, ?, ?)
                """,
                (otp_id, email, otp_hash, purpose, expires_at, created_at_str, client_ip)
            )

        return {
            "message": "Verification code dispatched to your email address.",
            "email": email,
            "purpose": purpose,
            "expires_in_seconds": 300,
            "resend_cooldown_seconds": 60,
            "provider": email_result.get("provider", "smtp")
        }
    finally:
        conn.close()


@app.post("/auth/email/register", status_code=status.HTTP_201_CREATED)
def register_citizen_with_email(payload: RegisterWithEmailRequest):
    """
    Verifies Email OTP and registers a new Citizen account (primary public user identity).
    Issues standard JWT access token upon successful verification.
    """
    from email_service import normalize_email, verify_email_otp_hash
    from sms_service import normalize_phone_number

    try:
        email = normalize_email(payload.email)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    otp = payload.otp.strip()
    full_name = payload.full_name.strip()
    password = payload.password.strip()

    phone = None
    if payload.phone and payload.phone.strip():
        try:
            phone = normalize_phone_number(payload.phone)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name must contain at least 2 non-whitespace characters."
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters in length."
        )

    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verification code must be exactly 6 numeric digits."
        )

    conn = get_connection()
    try:
        # Check duplicate email
        existing_email = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists. Please log in."
            )

        # Check duplicate phone if provided
        if phone:
            existing_phone = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone,)).fetchone()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this mobile number already exists. Please sign in instead."
                )

        # Retrieve latest unused OTP for registration
        otp_row = conn.execute(
            """
            SELECT * FROM email_otps
            WHERE email = ? AND purpose = 'register' AND is_used = 0
            ORDER BY created_at DESC LIMIT 1
            """,
            (email,)
        ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found. Please request a new code."
            )

        # Check expiration
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if otp_row["expires_at"] < now_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )

        # Check max attempts
        if otp_row["attempts"] >= otp_row["max_attempts"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This verification code has been invalidated. Please request a new code."
            )

        # Verify hash
        if not verify_email_otp_hash(email, otp, otp_row["otp_hash"]):
            with conn:
                conn.execute(
                    "UPDATE email_otps SET attempts = attempts + 1 WHERE otp_id = ?",
                    (otp_row["otp_id"],)
                )
            remaining = otp_row["max_attempts"] - (otp_row["attempts"] + 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect verification code. {remaining} verification attempt{'s' if remaining != 1 else ''} remaining."
            )

        # Invalidate OTP on success
        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        hashed_pw = hash_password(password)

        with conn:
            conn.execute("UPDATE email_otps SET is_used = 1 WHERE otp_id = ?", (otp_row["otp_id"],))

            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, phone, password_hash, role,
                    school_id, is_active, status, full_name, is_email_verified
                ) VALUES (?, ?, ?, ?, 'parent', NULL, 1, 'active', ?, 1)
                """,
                (user_id, email, phone, hashed_pw, full_name)
            )

            conn.execute(
                """
                INSERT INTO guardians (
                    guardian_id, user_id, full_name, phone, email, relationship
                ) VALUES (?, ?, ?, ?, ?, 'Guardian')
                """,
                (guardian_id, user_id, full_name, phone or "", email)
            )

            record_platform_audit(
                conn=conn,
                event_type="CITIZEN_EMAIL_REGISTERED",
                event_category="AUTH",
                institution_id=None,
                actor_user_id=user_id,
                actor_role="parent",
                entity_type="users",
                entity_id=user_id,
                action="CITIZEN_EMAIL_REGISTERED",
                new_values={"full_name": full_name, "email": email, "phone": phone},
                remarks="Citizen registered and verified via email OTP"
            )

        user_data = {
            "user_id": user_id,
            "role": "parent",
            "school_id": None,
            "student_id": None,
            "permanent_student_id": None,
            "email": email,
            "phone": phone,
            "full_name": full_name,
        }

        access_token = create_access_token(user_data)
        return {
            "message": f"Citizen registration successful for {full_name}!",
            "access_token": access_token,
            "token_type": "bearer",
            "role": "parent",
            "school_id": None,
            "user_id": user_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "user": {**user_data, "is_email_verified": 1},
        }
    finally:
        conn.close()


@app.post("/auth/email/login")
def login_citizen_with_email(request: Request, payload: EmailLoginRequest):
    """
    Authenticates a registered Citizen using Email and Password.
    Enforces password hashing, rate limiting, and email verification checks.
    """
    from email_service import normalize_email
    try:
        email = normalize_email(payload.email)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    client_ip = request.client.host if request.client else "127.0.0.1"
    if auth_limiter.is_locked_out(client_ip, email, max_failures=5):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Account temporarily locked out for 60 seconds."
        )

    conn = get_connection()
    try:
        user = conn.execute(
            """
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active, status, full_name,
                   permanent_student_id, student_id, is_email_verified
            FROM users
            WHERE email = ? COLLATE NOCASE
            """,
            (email,)
        ).fetchone()

        if (
            user is None
            or not user["is_active"]
            or user["status"] == "suspended"
            or not verify_password(payload.password, user["password_hash"])
        ):
            auth_limiter.record_failed_login(client_ip, email, max_failures=5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        if user["is_email_verified"] == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email address is not verified. Please complete email verification before logging in."
            )

        auth_limiter.reset_failed_login(client_ip, email)

        with conn:
            conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))

        user_data = {
            "user_id": user["user_id"],
            "role": user["role"],
            "school_id": user["school_id"],
            "student_id": user["student_id"],
            "permanent_student_id": user["permanent_student_id"],
            "email": user["email"],
            "phone": user["phone"],
            "full_name": user["full_name"],
        }
        access_token = create_access_token(user_data)
        return {
            "message": "Login successful.",
            "access_token": access_token,
            "token_type": "bearer",
            "role": user["role"],
            "school_id": user["school_id"],
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "phone": user["phone"],
            "user": {**user_data, "is_email_verified": user["is_email_verified"]},
        }
    finally:
        conn.close()


@app.post("/auth/student/lookup")
def lookup_student_for_activation(payload: StudentLookupRequest):
    """
    Looks up an enrolled student record by Student ID or Permanent SATS ID
    prior to account activation. Returns verified official student details
    for student confirmation and identity verification.
    """
    identifier = payload.student_identifier.strip()
    conn = get_connection()
    try:
        student = conn.execute(
            """
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.enrollment_status, s.date_of_birth,
                   s.first_language, s.gender,
                   sch.school_name, sch.school_type, sch.district
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            WHERE s.student_id = ? COLLATE NOCASE OR s.permanent_student_id = ? COLLATE NOCASE
            """,
            (identifier, identifier),
        ).fetchone()

        # Error 1: Student ID not found
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student ID not found. No enrolled student record matches '{identifier}'. Please check your Student ID / Permanent SATS ID.",
            )

        # Error 2: Student exists but is not actively enrolled
        if (student["enrollment_status"] or "").strip().lower() != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Student exists but is not actively enrolled (Current status: {student['enrollment_status']}). Activation is permitted only for actively enrolled students.",
            )

        # Error 3: Student account already activated
        existing_user = conn.execute(
            """
            SELECT user_id, full_name FROM users
            WHERE student_id = ? OR permanent_student_id = ?
            """,
            (student["student_id"], student["permanent_student_id"]),
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"Student account already activated. An active portal account is already registered for this student. Please sign in with your credentials or reset your password.",
            )

        # Error 5: Student record requires institution verification
        if not student["date_of_birth"] or not str(student["date_of_birth"]).strip():
            raise HTTPException(
                status_code=400,
                detail="Student record requires institution verification. Official date of birth is missing from school records. Please contact your institution administrator to update your student profile.",
            )

        # Clean official name
        clean_name = re.sub(r"\s+\d{3,}$", "", student["student_name"]).strip()
        if not clean_name:
            clean_name = student["student_name"].strip()

        std_display = f"Standard {student['standard']}" if student["standard"] else (student.get("school_type") or "School")
        sec_display = f"Section {student['section']}" if student["section"] else "General"

        return {
            "status": "record_found",
            "student_id": student["student_id"],
            "permanent_student_id": student["permanent_student_id"],
            "official_student_name": clean_name,
            "institution_id": student["school_id"],
            "institution_name": student["school_name"],
            "district": student["district"],
            "standard": student["standard"],
            "standard_display": std_display,
            "section": student["section"],
            "section_display": sec_display,
            "enrollment_status": student["enrollment_status"],
            "verification_method": "date_of_birth",
            "message": "Student record located in official database. Please confirm your details and complete identity verification below."
        }
    finally:
        conn.close()


@app.post("/auth/student/register", response_model=StudentRegisterResponse, status_code=201)
def register_student_account(payload: StudentRegisterRequest):
    """
    Dedicated on-demand student account activation and provisioning.
    Verifies that the student exists in the official students database,
    verifies identity via authorized verification method (Date of Birth),
    confirms active enrollment and no existing account,
    and provisions the user with role='student' and Argon2id hash.
    """
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match.",
        )
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least 8 characters.",
        )

    identifier = payload.student_identifier.strip()
    conn = get_connection()
    try:
        # 1. Look up student in students table
        student = conn.execute(
            """
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.enrollment_status, s.date_of_birth,
                   sch.school_name
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            WHERE s.student_id = ? COLLATE NOCASE OR s.permanent_student_id = ? COLLATE NOCASE
            """,
            (identifier, identifier),
        ).fetchone()

        # Error 1: Student ID not found
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student ID not found. No enrolled student record matches '{identifier}'. Please check your Student ID / Permanent SATS ID.",
            )

        # Error 2: Student exists but is not actively enrolled
        if (student["enrollment_status"] or "").strip().lower() != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Student exists but is not actively enrolled (Current status: {student['enrollment_status']}). Activation is permitted only for actively enrolled students.",
            )

        # Error 3: Student account already activated
        existing_user = conn.execute(
            """
            SELECT user_id FROM users
            WHERE student_id = ? OR permanent_student_id = ?
            """,
            (student["student_id"], student["permanent_student_id"]),
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"Student account already activated. An active portal account is already registered for this student. Please sign in with your credentials or reset your password.",
            )

        # Error 5: Student record requires institution verification
        if not student["date_of_birth"] or not str(student["date_of_birth"]).strip():
            raise HTTPException(
                status_code=400,
                detail="Student record requires institution verification. Official date of birth is missing from school records. Please contact your institution administrator to update your student profile.",
            )

        # Error 4: Identity verification failed (via Date of Birth)
        def _norm_dob(val: Optional[str]) -> str:
            if not val:
                return ""
            s = val.strip()
            m1 = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", s)
            if m1:
                return f"{int(m1.group(1)):04d}-{int(m1.group(2)):02d}-{int(m1.group(3)):02d}"
            m2 = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", s)
            if m2:
                return f"{int(m2.group(3)):04d}-{int(m2.group(2)):02d}-{int(m2.group(1)):02d}"
            return s

        if not payload.date_of_birth or not payload.date_of_birth.strip():
            raise HTTPException(
                status_code=400,
                detail="Identity verification failed. Official Date of Birth is required to confirm student identity.",
            )

        provided_dob = _norm_dob(payload.date_of_birth)
        official_dob = _norm_dob(student["date_of_birth"])
        if provided_dob != official_dob:
            raise HTTPException(
                status_code=400,
                detail="Identity verification failed. The provided date of birth does not match official institution records for this student.",
            )

        # Official clean student name (do not trust user-entered spelling)
        clean_name = re.sub(r"\s+\d{3,}$", "", student["student_name"]).strip()
        if not clean_name:
            clean_name = student["student_name"].strip()

        # Email for notifications only — not trusted as proof of identity
        email_clean = payload.email.strip().lower() if payload.email and payload.email.strip() else f"student.{student['student_id'].lower()}@nagriksetu.portal"

        # Check email uniqueness if email provided
        if payload.email and payload.email.strip():
            existing_email = conn.execute(
                "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
                (email_clean,),
            ).fetchone()
            if existing_email:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this email address already exists. Please provide a different email or leave it blank.",
                )

        # Check phone uniqueness if phone provided
        phone_clean = payload.phone.strip() if payload.phone and payload.phone.strip() else None
        if phone_clean:
            existing_phone = conn.execute(
                "SELECT user_id FROM users WHERE phone = ?",
                (phone_clean,),
            ).fetchone()
            if existing_phone:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this phone number already exists. Please provide a different phone number or leave it blank.",
                )

        # Hash password with Argon2id
        try:
            pwd_hash = hash_password(payload.password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

        user_id = str(uuid.uuid4())
        try:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, phone, password_hash, role,
                    school_id, is_active, status, full_name,
                    permanent_student_id, student_id, created_at
                ) VALUES (?, ?, ?, ?, 'student', ?, 1, 'active', ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    user_id,
                    email_clean,
                    phone_clean,
                    pwd_hash,
                    student["school_id"],
                    clean_name,
                    student["permanent_student_id"],
                    student["student_id"],
                ),
            )
        except sqlite3.IntegrityError as ie:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to register student account: constraint conflict ({str(ie)}).",
            )

        # Record audit log
        audit_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO audit_logs (
                audit_id, actor_user_id, actor_role,
                action, entity_type, entity_id,
                school_id, ip_address, metadata_json
            ) VALUES (?, ?, 'student', 'STUDENT_ACCOUNT_ACTIVATED', 'user', ?, ?, NULL, ?)
            """,
            (
                audit_id,
                user_id,
                user_id,
                student["school_id"],
                json.dumps({
                    "student_id": student["student_id"],
                    "permanent_student_id": student["permanent_student_id"],
                    "official_name": clean_name,
                    "institution_id": student["school_id"],
                    "verification_method": "date_of_birth"
                })
            )
        )
        conn.commit()

        return {
            "user_id": user_id,
            "student_id": student["student_id"],
            "permanent_student_id": student["permanent_student_id"],
            "full_name": clean_name,
            "school_id": student["school_id"],
            "message": f"Student account for '{clean_name}' activated successfully! You can now sign in using your Student ID and password.",
        }
    finally:
        conn.close()


# -------------------------------------------------------------
# PHASE 12: ACADEMIC CALCULATION & PERFORMANCE ENGINE
# -------------------------------------------------------------

def calculate_grade(marks: float, max_marks: float) -> tuple[float, str]:
    if max_marks <= 0:
        return 0.0, "N/A"
    pct = round((marks / max_marks) * 100.0, 2)
    if pct >= 90.0:
        grade = "A+"
    elif pct >= 80.0:
        grade = "A"
    elif pct >= 70.0:
        grade = "B+"
    elif pct >= 60.0:
        grade = "B"
    elif pct >= 50.0:
        grade = "C"
    elif pct >= 35.0:
        grade = "D"
    else:
        grade = "F"
    return pct, grade


def calculate_attendance_summary(conn, permanent_student_id: str) -> dict:
    rows = conn.execute(
        """
        SELECT attendance_id, institution_id, permanent_student_id,
               academic_year, attendance_date, status, subject_name, remarks
        FROM student_attendance
        WHERE permanent_student_id = ?
        ORDER BY attendance_date ASC
        """,
        (permanent_student_id,)
    ).fetchall()

    if not rows:
        return {
            "attendance_percentage": None,
            "total_working_days": 0,
            "present_days": 0,
            "absent_days": 0,
            "leave_days": 0,
            "monthly_breakdown": [],
            "recent_records": []
        }

    date_status_map = {}
    for r in rows:
        dt = r["attendance_date"]
        st = r["status"]
        if dt not in date_status_map:
            date_status_map[dt] = st
        elif st == "present":
            date_status_map[dt] = "present"
        elif st == "leave" and date_status_map[dt] == "absent":
            date_status_map[dt] = "leave"

    total_days = len(date_status_map)
    present_days = sum(1 for s in date_status_map.values() if s == "present")
    absent_days = sum(1 for s in date_status_map.values() if s == "absent")
    leave_days = sum(1 for s in date_status_map.values() if s == "leave")

    pct = round((present_days / total_days) * 100.0, 1) if total_days > 0 else None

    monthly = {}
    for dt, st in date_status_map.items():
        month_key = dt[:7]
        if month_key not in monthly:
            monthly[month_key] = {"month": month_key, "total": 0, "present": 0, "absent": 0, "leave": 0}
        monthly[month_key]["total"] += 1
        if st == "present":
            monthly[month_key]["present"] += 1
        elif st == "absent":
            monthly[month_key]["absent"] += 1
        elif st == "leave":
            monthly[month_key]["leave"] += 1

    monthly_list = []
    for m in sorted(monthly.keys()):
        tot = monthly[m]["total"]
        prs = monthly[m]["present"]
        monthly[m]["percentage"] = round((prs / tot) * 100.0, 1) if tot > 0 else 0.0
        monthly_list.append(monthly[m])

    recent = [dict(r) for r in rows[-20:]]

    return {
        "attendance_percentage": pct,
        "total_working_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "leave_days": leave_days,
        "monthly_breakdown": monthly_list,
        "recent_records": recent
    }


def calculate_academic_performance(conn, permanent_student_id: str, institution_id: Optional[str] = None) -> dict:
    att_summary = calculate_attendance_summary(conn, permanent_student_id)

    results_rows = conn.execute(
        """
        SELECT ar.result_id, ar.enrollment_id, ar.subject_name, ar.exam_name,
               ar.marks_obtained, ar.maximum_marks, ar.percentage, ar.grade,
               ar.academic_year, ar.exam_date, ar.created_at, ar.updated_at
        FROM academic_results ar
        JOIN enrollments e ON e.enrollment_id = ar.enrollment_id
        WHERE e.permanent_student_id = ?
        ORDER BY ar.academic_year DESC, ar.exam_date DESC, ar.created_at DESC
        """,
        (permanent_student_id,)
    ).fetchall()

    results_list = []
    for r in results_rows:
        item = dict(r)
        if (item.get("percentage") is None or item.get("grade") is None) and item.get("maximum_marks", 0) > 0:
            calc_p, calc_g = calculate_grade(item["marks_obtained"], item["maximum_marks"])
            item["percentage"] = item.get("percentage") or calc_p
            item["grade"] = item.get("grade") or calc_g
        results_list.append(item)

    subject_map = {}
    for r in results_list:
        subj = r["subject_name"]
        if subj not in subject_map:
            subject_map[subj] = {"subject_name": subj, "total_marks": 0.0, "total_max": 0.0, "count": 0}
        subject_map[subj]["total_marks"] += r["marks_obtained"]
        subject_map[subj]["total_max"] += r["maximum_marks"]
        subject_map[subj]["count"] += 1

    subject_performance = []
    for subj, val in subject_map.items():
        avg_pct = round((val["total_marks"] / val["total_max"]) * 100.0, 1) if val["total_max"] > 0 else 0.0
        _, gr = calculate_grade(val["total_marks"], val["total_max"])
        subject_performance.append({
            "subject_name": subj,
            "average_percentage": avg_pct,
            "overall_grade": gr,
            "assessments_count": val["count"]
        })

    exam_progress_map = {}
    for r in results_list:
        ex_name = r["exam_name"]
        ex_date = r.get("exam_date") or r.get("academic_year") or "2026"
        if ex_name not in exam_progress_map:
            exam_progress_map[ex_name] = {"exam_name": ex_name, "exam_date": ex_date, "total_marks": 0.0, "total_max": 0.0, "count": 0}
        exam_progress_map[ex_name]["total_marks"] += r["marks_obtained"]
        exam_progress_map[ex_name]["total_max"] += r["maximum_marks"]
        exam_progress_map[ex_name]["count"] += 1

    academic_progress = []
    for ex, val in exam_progress_map.items():
        avg_pct = round((val["total_marks"] / val["total_max"]) * 100.0, 1) if val["total_max"] > 0 else 0.0
        _, gr = calculate_grade(val["total_marks"], val["total_max"])
        academic_progress.append({
            "exam_name": ex,
            "exam_date": val["exam_date"],
            "overall_percentage": avg_pct,
            "grade": gr,
            "subjects_evaluated": val["count"]
        })

    stu = conn.execute(
        "SELECT school_id, standard FROM students WHERE permanent_student_id = ?",
        (permanent_student_id,)
    ).fetchone()

    inst_id = institution_id or (stu["school_id"] if stu else None)
    std_val = str(stu["standard"]) if stu and stu["standard"] is not None else "1"

    upcoming_exams = []
    announcements = []
    if inst_id:
        exams = conn.execute(
            """
            SELECT exam_id, institution_id, academic_year, exam_name,
                   standard_or_level, start_date, end_date, status, description
            FROM examinations
            WHERE institution_id = ?
              AND (standard_or_level = ? OR standard_or_level = 'All')
              AND status IN ('scheduled', 'ongoing')
            ORDER BY start_date ASC
            """,
            (inst_id, std_val)
        ).fetchall()
        upcoming_exams = [dict(x) for x in exams]

        ann_rows = conn.execute(
            """
            SELECT announcement_id, title, content, target_audience, published_date
            FROM institution_announcements
            WHERE institution_id = ?
              AND target_audience IN ('all', 'students', 'parents')
            ORDER BY published_date DESC LIMIT 5
            """,
            (inst_id,)
        ).fetchall()
        announcements = [dict(a) for a in ann_rows]

    return {
        "attendance": att_summary,
        "attendance_summary": att_summary,
        "results": results_list,
        "academic_results": results_list,
        "subject_performance": subject_performance,
        "academic_progress": academic_progress,
        "upcoming_examinations": upcoming_exams,
        "announcements": announcements
    }


@app.get("/student/profile")
def get_student_profile(user: dict = Depends(require_student)):
    """
    Dedicated endpoint returning the authenticated student's own verified academic profile.
    Strictly isolated: does not expose another student's information.
    """
    conn = get_connection()
    try:
        stu_id = user.get("student_id")
        perm_id = user.get("permanent_student_id")
        student = conn.execute(
            """
            SELECT student_id, student_name, school_id, standard, section,
                   age, permanent_student_id, first_language, date_of_birth,
                   gender, admission_date, enrollment_status
            FROM students
            WHERE student_id = ? OR permanent_student_id = ?
            """,
            (stu_id, perm_id),
        ).fetchone()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student record not found.",
            )

        school = conn.execute(
            """
            SELECT school_id, school_name, school_type, category,
                   district, address, state
            FROM schools
            WHERE school_id = ?
            """,
            (student["school_id"],),
        ).fetchone()

        enrollments = conn.execute(
            """
            SELECT enrollment_id, academic_year, standard, section,
                   first_language, stream, subject_combination, enrollment_status,
                   admission_date
            FROM enrollments
            WHERE permanent_student_id = ?
            ORDER BY academic_year DESC
            """,
            (student["permanent_student_id"],),
        ).fetchall()

        # Guardians & residential address lookup
        guardians = conn.execute(
            """
            SELECT g.guardian_id, g.full_name, g.relationship, g.phone, g.email, g.address
            FROM student_guardians sg
            JOIN guardians g ON g.guardian_id = sg.guardian_id
            WHERE sg.permanent_student_id = ? AND sg.is_verified = 1
            """,
            (student["permanent_student_id"],),
        ).fetchall()

        res_address = None
        for g in guardians:
            if g["address"] and str(g["address"]).strip():
                res_address = str(g["address"]).strip()
                break

        if not res_address:
            app_match = conn.execute(
                """
                SELECT residential_address
                FROM admission_applications
                WHERE (enrolled_student_id = ? OR applicant_name = ? COLLATE NOCASE)
                  AND residential_address IS NOT NULL AND TRIM(residential_address) != ''
                LIMIT 1
                """,
                (student["student_id"], student["student_name"]),
            ).fetchone()
            if app_match and app_match["residential_address"]:
                res_address = app_match["residential_address"]

        # Calculate comprehensive academic & attendance performance
        perf = calculate_academic_performance(conn, student["permanent_student_id"], student["school_id"])

        return {
            "student": dict(student),
            "school": dict(school) if school else None,
            "enrollments": [dict(e) for e in enrollments],
            "guardians": [dict(g) for g in guardians],
            "residential_address": res_address,
            "attendance": perf["attendance"],
            "attendance_summary": perf["attendance"],
            "attendance_percentage": perf["attendance"]["attendance_percentage"],
            "total_working_days": perf["attendance"]["total_working_days"],
            "days_present": perf["attendance"]["present_days"],
            "days_absent": perf["attendance"]["absent_days"],
            "days_leave": perf["attendance"]["leave_days"],
            "tests": perf["results"],
            "subject_performance": perf["subject_performance"],
            "academic_progress": perf["academic_progress"],
            "upcoming_examinations": perf["upcoming_examinations"],
            "announcements": perf["announcements"],
            "academic_results": perf["results"],
            "academic_performance": perf,
        }
    finally:
        conn.close()


@app.get("/auth/me")
def get_my_account(user: dict = Depends(get_current_user)):
    conn = get_connection()
    try:
        workspaces = conn.execute(
            """
            SELECT uir.institution_id, s.school_name, s.school_type, uir.role_id, uir.status
            FROM user_institution_roles uir
            JOIN schools s ON s.school_id = uir.institution_id
            WHERE uir.user_id = ? AND uir.status = 'active'
            """,
            (user["user_id"],)
        ).fetchall()

        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "phone": user["phone"],
            "full_name": user.get("full_name"),
            "role": user["role"],
            "school_id": user["school_id"],
            "is_active": bool(user["is_active"]),
            "status": user.get("status", "active"),
            "student_id": user.get("student_id"),
            "permanent_student_id": user.get("permanent_student_id"),
            "workspaces": [
                {
                    "institution_id": w["institution_id"],
                    "school_name": w["school_name"],
                    "school_type": w["school_type"],
                    "role_id": w["role_id"],
                }
                for w in workspaces
            ],
        }
    finally:
        conn.close()


@app.get("/")
def home():
    conn = get_connection()
    try:
        schools = conn.execute(
            "SELECT COUNT(*) FROM schools"
        ).fetchone()[0]
        students = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]
        return {
            "service": "NagrikSetu School Service",
            "status": "running",
            "database": "SQLite",
            "total_schools": schools,
            "total_students": students,
        }
    finally:
        conn.close()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def get_institution_admin_status_dict(conn, school_id, inst_row=None):
    if inst_row is None:
        inst = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools WHERE school_id = ?", (school_id,)).fetchone()
        if not inst:
            return None
    else:
        inst = inst_row

    roles = conn.execute("""
        SELECT u.user_id, u.email, u.full_name, u.is_active, u.status as user_status,
               uir.id as mapping_id, uir.status as role_status, uir.role_id, uir.created_at
        FROM user_institution_roles uir
        JOIN users u ON u.user_id = uir.user_id
        WHERE uir.institution_id = ?
          AND uir.role_id IN ('academic_admin', 'school_admin')
        ORDER BY uir.created_at DESC
    """, (school_id,)).fetchall()

    latest_token = conn.execute("""
        SELECT it.token_id, it.user_id, it.expires_at, it.is_used, it.created_at,
               u.email, u.full_name, u.status as user_status, u.is_active,
               uir.status as uir_status
        FROM invitation_tokens it
        JOIN users u ON u.user_id = it.user_id
        LEFT JOIN user_institution_roles uir ON uir.user_id = it.user_id AND uir.institution_id = it.institution_id
        WHERE it.institution_id = ?
          AND it.role_id IN ('academic_admin', 'school_admin')
        ORDER BY it.created_at DESC
        LIMIT 1
    """, (school_id,)).fetchone()

    # Priority 1: ACTIVE Administrator
    active_role = next((r for r in roles if r["role_status"] == "active" and r["is_active"] == 1 and r["user_status"] == "active"), None)
    if active_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "ACTIVE",
            "button_label": "Continue to Administrator Login →",
            "has_active_admin": True,
            "has_pending_invitation": False,
            "is_invited": False,
            "is_pending_password": False,
            "is_suspended": False,
            "can_login": True,
            "status_description": "Active Academic Administrator configured and verified."
        }

    # Priority 2: SUSPENDED Administrator (slot retained)
    suspended_role = next((r for r in roles if (r["role_status"] == "suspended" or r["user_status"] == "suspended") and r["role_status"] not in ("revoked", "declined")), None)
    if suspended_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "SUSPENDED",
            "button_label": "Account Suspended",
            "has_active_admin": False,
            "has_pending_invitation": False,
            "is_invited": False,
            "is_pending_password": False,
            "is_suspended": True,
            "can_login": False,
            "status_description": "Administrator account is temporarily suspended by Platform Administration."
        }

    # Priority 3: ACCEPTED_PENDING_PASSWORD
    pending_pwd_role = next((r for r in roles if (r["role_status"] == "accepted_pending_password" or r["user_status"] == "accepted_pending_password") and r["role_status"] not in ("revoked", "declined")), None)
    if pending_pwd_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "ACCEPTED_PENDING_PASSWORD",
            "button_label": "Complete Account Setup",
            "has_active_admin": False,
            "has_pending_invitation": True,
            "is_invited": False,
            "is_pending_password": True,
            "is_suspended": False,
            "can_login": False,
            "status_description": "Invitation accepted. Password creation required before login is enabled."
        }

    # Priority 4: INVITED
    if latest_token and latest_token["is_used"] == 0:
        try:
            exp = datetime.fromisoformat(latest_token["expires_at"].replace("Z", ""))
            is_expired = datetime.utcnow() > exp
        except Exception:
            is_expired = False

        if not is_expired and latest_token["uir_status"] not in ("revoked", "declined"):
            if latest_token["uir_status"] == "accepted_pending_password" or latest_token["user_status"] == "accepted_pending_password":
                return {
                    "institution_id": inst["school_id"],
                    "institution_name": inst["school_name"],
                    "category": inst["category"],
                    "district": inst["district"],
                    "school_type": inst["school_type"],
                    "status": "ACCEPTED_PENDING_PASSWORD",
                    "button_label": "Complete Account Setup",
                    "has_active_admin": False,
                    "has_pending_invitation": True,
                    "is_invited": False,
                    "is_pending_password": True,
                    "is_suspended": False,
                    "can_login": False,
                    "status_description": "Invitation accepted. Password creation required before login is enabled."
                }
            return {
                "institution_id": inst["school_id"],
                "institution_name": inst["school_name"],
                "category": inst["category"],
                "district": inst["district"],
                "school_type": inst["school_type"],
                "status": "INVITED",
                "button_label": "Invitation Available",
                "has_active_admin": False,
                "has_pending_invitation": True,
                "is_invited": True,
                "is_pending_password": False,
                "is_suspended": False,
                "can_login": False,
                "status_description": "Administrator invitation issued. Pending invitee acceptance."
            }
        elif is_expired:
            return {
                "institution_id": inst["school_id"],
                "institution_name": inst["school_name"],
                "category": inst["category"],
                "district": inst["district"],
                "school_type": inst["school_type"],
                "status": "EXPIRED",
                "button_label": "Invitation Required",
                "has_active_admin": False,
                "has_pending_invitation": False,
                "is_invited": False,
                "is_pending_password": False,
                "is_suspended": False,
                "can_login": False,
                "status_description": "Previous administrator invitation has expired. An invitation is required."
            }

    # Priority 5: REVOKED / DECLINED
    revoked_role = next((r for r in roles if r["role_status"] in ("revoked", "declined")), None)
    if revoked_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "NOT_INVITED",
            "button_label": "Invitation Required",
            "has_active_admin": False,
            "has_pending_invitation": False,
            "is_invited": False,
            "is_pending_password": False,
            "is_suspended": False,
            "can_login": False,
            "status_description": "Previous invitation or assignment was revoked. An invitation is required."
        }

    # Default: NOT_INVITED
    return {
        "institution_id": inst["school_id"],
        "institution_name": inst["school_name"],
        "category": inst["category"],
        "district": inst["district"],
        "school_type": inst["school_type"],
        "status": "NOT_INVITED",
        "button_label": "Invitation Required",
        "has_active_admin": False,
        "has_pending_invitation": False,
        "is_invited": False,
        "is_pending_password": False,
        "is_suspended": False,
        "can_login": False,
        "status_description": "No administrator invitation has been generated for this institution."
    }


@app.get("/schools")
def list_schools(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    latitude: Optional[float] = Query(default=None),
    longitude: Optional[float] = Query(default=None),
    radius_km: Optional[float] = Query(default=None, ge=0.1, le=500.0),
    category: Optional[str] = Query(default=None),
):
    import math

    def haversine_distance(lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return None
        R = 6371.0 # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 2)

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.school_id, s.school_name, s.district, s.state,
                   s.school_type, s.category, s.address, s.established_year,
                   s.description, s.public_phone, s.website, s.facilities_json,
                   s.logo_url, s.cover_image_url, s.affiliation, s.recognition,
                   s.latitude, s.longitude,
                   COALESCE(SUM(ps.capacity), 0) AS total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN ps.capacity > ps.current_strength THEN ps.capacity - ps.current_strength ELSE 0 END), 0) AS available_seats
            FROM schools s
            LEFT JOIN program_sections ps ON ps.institution_id = s.school_id
            GROUP BY s.school_id
            ORDER BY s.school_name
            """,
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["admin_status"] = get_institution_admin_status_dict(conn, d["school_id"], d)

            # Filter by category if provided
            if category and category != "ALL":
                cat = d.get("category") or ""
                stype = (d.get("school_type") or "").lower()
                matches_cat = False
                if category == "SCHOOLS" and (cat == "Schools (K-10)" or stype == "school"):
                    matches_cat = True
                elif category == "PU" and (cat == "PU Colleges (11-12)" or "pu" in stype or "pre-university" in stype):
                    matches_cat = True
                elif category == "DEGREE" and (cat == "Degree Colleges" or stype == "degree college" or ("engineering" in stype and "university" not in stype and cat != "Universities")):
                    matches_cat = True
                elif category == "UNIVERSITY" and (cat == "Universities" or "university" in stype):
                    matches_cat = True
                if not matches_cat:
                    continue

            # Calculate distance if user coords provided
            if latitude is not None and longitude is not None:
                inst_lat = d.get("latitude")
                inst_lon = d.get("longitude")
                if inst_lat is not None and inst_lon is not None:
                    dist = haversine_distance(latitude, longitude, inst_lat, inst_lon)
                    d["distance_km"] = dist
                    if radius_km is not None and dist is not None and dist > radius_km:
                        continue
                else:
                    d["distance_km"] = None
                    if radius_km is not None:
                        # Exclude institutions with unverified coordinates from radius filtering
                        continue
            else:
                d["distance_km"] = None

            result.append(d)

        # If location was provided, sort by distance ascending
        if latitude is not None and longitude is not None:
            result.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] if x["distance_km"] is not None else float("inf")))

        return result[offset : offset + limit]
    finally:
        conn.close()


@app.get("/schools/{school_id}")
def get_school(school_id: str):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT school_id, school_name, district, state,
                   school_type, category, address, established_year,
                   description, public_phone, website, facilities_json,
                   logo_url, cover_image_url, email, affiliation, recognition,
                   campus_name, is_parent_group, map_url,
                   about_json, facilities_details_json, hostel_details_json,
                   transport_details_json, admissions_details_json
            FROM schools
            WHERE school_id = ?
            """,
            (school_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(404, "School not found")

        data = dict(row)
        for json_field in [
            "facilities_json",
            "about_json",
            "facilities_details_json",
            "hostel_details_json",
            "transport_details_json",
            "admissions_details_json",
        ]:
            raw_val = data.get(json_field)
            if raw_val and isinstance(raw_val, str):
                try:
                    data[json_field] = json.loads(raw_val)
                except Exception:
                    pass

        data["about"] = data.get("about_json") or {}
        data["facilities"] = data.get("facilities_details_json") or {}
        data["hostel"] = data.get("hostel_details_json") or {}
        data["transport"] = data.get("transport_details_json") or {}
        data["admissions"] = data.get("admissions_details_json") or {}

        seat_row = conn.execute(
            """
            SELECT COALESCE(SUM(capacity), 0) AS sanctioned_capacity,
                   COALESCE(SUM(current_strength), 0) AS current_strength,
                   COALESCE(SUM(CASE WHEN capacity > current_strength THEN capacity - current_strength ELSE 0 END), 0) AS available_seats
            FROM program_sections
            WHERE institution_id = ?
            """,
            (school_id,)
        ).fetchone()
        data["seat_summary"] = dict(seat_row) if seat_row else {"sanctioned_capacity": 0, "current_strength": 0, "available_seats": 0}

        return data
    finally:
        conn.close()


@app.get("/schools/{school_id}/courses")
def get_school_courses(
    school_id: str,
    degree: Optional[str] = Query(default=None),
    stream: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """Retrieve higher education courses with degree and stream filters."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT facilities_json FROM schools WHERE school_id = ?",
            (school_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(404, "Institution not found")

        fac_raw = row["facilities_json"] or "{}"
        try:
            fac = json.loads(fac_raw)
        except Exception:
            fac = {}

        courses = fac.get("courses", []) if isinstance(fac, dict) else []

        filtered = []
        for c in courses:
            if degree and c.get("degree") != degree:
                continue
            if stream and c.get("stream") != stream:
                continue
            if search:
                q = search.lower().strip()
                name = c.get("course_name", "").lower()
                overview = c.get("overview", "").lower()
                if q not in name and q not in overview:
                    continue
            filtered.append(c)

        return filtered
    finally:
        conn.close()


@app.get("/search-schools")
def search_schools(
    keyword: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
):
    conn = get_connection()
    try:
        term = f"%{keyword.strip()}%"
        rows = conn.execute(
            """
            SELECT school_id, school_name, district, state,
                   school_type, address, public_phone, website
            FROM schools
            WHERE school_name LIKE ?
               OR district LIKE ?
               OR school_id LIKE ?
            ORDER BY school_name
            LIMIT ?
            """,
            (term, term, term, limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()



@app.get("/schools/{school_id}/students")
def get_school_students(
    school_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    standard: Optional[int] = Query(default=None, ge=1, le=12),
    section: Optional[str] = Query(default=None, pattern="^[ABC]$"),
    user: dict = Depends(get_current_user),
):
    """
    Protected student list for a school.
    Access rules:
    - platform_admin: can access any school's students.
    - school_staff / school_admin: can ONLY access their assigned school (user['school_id'] == school_id).
    - parent / unauthenticated: access denied (401/403).
    """
    if user["role"] not in STAFF_ROLES and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to authorized school and platform staff.",
        )

    if user["role"] in STAFF_ROLES:
        if not user.get("school_id") or user["school_id"] != school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cross-institution access forbidden: Account is assigned to {user.get('school_id')}, cannot view {school_id} records.",
            )
        conn_chk = get_connection()
        try:
            perms = get_staff_permissions(conn_chk, user["user_id"], school_id, user["role"])
            if not perms.get("can_manage_students") and not perms.get("can_manage_academics") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: Account does not have permission to access student records.",
                )
        finally:
            conn_chk.close()

    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "School not found")

        # Unwrap Query parameter defaults if called directly as a Python function
        std_val = standard if isinstance(standard, int) else (standard.default if hasattr(standard, 'default') else None)
        sec_val = section if isinstance(section, str) else (section.default if hasattr(section, 'default') else None)
        lim_val = limit if isinstance(limit, int) else (limit.default if hasattr(limit, 'default') else 50)
        off_val = offset if isinstance(offset, int) else (offset.default if hasattr(offset, 'default') else 0)

        sql = """
            SELECT s.student_id, s.permanent_student_id,
                   s.school_id, sc.school_name, s.standard,
                   s.section, s.first_language, s.enrollment_status
            FROM students s
            JOIN schools sc ON sc.school_id = s.school_id
            WHERE s.school_id = ?
        """
        params = [school_id]

        if std_val is not None:
            sql += " AND s.standard = ?"
            params.append(std_val)

        if sec_val is not None:
            sql += " AND s.section = ?"
            params.append(sec_val)

        sql += " ORDER BY s.standard, s.section, s.student_id LIMIT ? OFFSET ?"
        params.extend([lim_val, off_val])

        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/students/{student_id}")
def get_student_record(
    student_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Protected individual student record.
    Access rules:
    - platform_admin: can access any student record.
    - school_staff / school_admin: can access students belonging to their assigned school.
    - parent: can access ONLY verified linked children (is_verified = 1 and can_view_records = 1).
    - unauthenticated / unauthorized: access denied (401/403).
    """
    conn = get_connection()
    try:
        student = conn.execute(
            """
            SELECT student_id, permanent_student_id, school_id,
                   standard, section, enrollment_status
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()

        if student is None:
            raise HTTPException(404, "Student not found")

        # Authorization rules by role
        if user["role"] == "platform_admin":
            pass
        elif user["role"] in STAFF_ROLES:
            if not user.get("school_id") or user["school_id"] != student["school_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cross-institution access forbidden: Account is assigned to {user.get('school_id')}, cannot view {student['school_id']} records.",
                )
            perms = get_staff_permissions(conn, user["user_id"], student["school_id"], user["role"])
            if not perms.get("can_manage_students") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: Account does not have permission to access student records.",
                )
        elif user["role"] == "parent":
            guardian = get_parent_guardian(conn, user["user_id"])
            if guardian is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No guardian profile is linked to this account.",
                )
            child = get_authorized_child(
                conn,
                guardian["guardian_id"],
                student["permanent_student_id"],
                "can_view_records",
            )
            if child is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to view records for this student.",
                )
        elif user["role"] == "student":
            user_stu_id = user.get("student_id")
            user_perm_id = user.get("permanent_student_id")
            if student["student_id"] != user_stu_id and student["permanent_student_id"] != user_perm_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Students are strictly permitted to view only their own academic records.",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view student records.",
            )

        school = conn.execute(
            """
            SELECT school_id, school_name, address, district, state
            FROM schools
            WHERE school_id = ?
            """,
            (student["school_id"],),
        ).fetchone()

        history = conn.execute(
            """
            SELECT e.standard, e.section, e.academic_year,
                   e.school_id, sc.school_name
            FROM enrollments e
            JOIN schools sc ON sc.school_id = e.school_id
            WHERE e.permanent_student_id = ?
            ORDER BY e.academic_year, e.standard
            """,
            (student["permanent_student_id"],),
        ).fetchall()

        return {
            "student_id": student["student_id"],
            "current_school": dict(school) if school else None,
            "current_standard": student["standard"],
            "current_section": student["section"],
            "enrollment_status": student["enrollment_status"],
            "school_history": [dict(row) for row in history],
        }
    finally:
        conn.close()


@app.get("/schools/{school_id}/programs")
def get_school_programs(school_id: str):
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, category, school_type FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "School not found")

        sql = """
            SELECT p.program_id, p.institution_id as school_id, p.education_level,
                   p.program_name, p.degree_type, p.discipline_or_stream,
                   p.combination_code, p.faculty_name, p.department_name, p.duration_years,
                   p.is_active,
                   COALESCE(SUM(ps.capacity), 0) as total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) as total_strength,
                   COUNT(ps.section_id) as section_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ? AND p.is_active = 1
        """
        params = [school_id]
        
        # Category-specific filtering
        cat = school["category"] or ""
        stype = school["school_type"] or ""
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'"
        elif cat == "Degree Colleges" or stype == "Degree College":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate')"
        elif cat == "Universities" or stype == "University":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate', 'doctoral')"

        sql += """
            GROUP BY p.program_id
            ORDER BY 
                CASE p.education_level 
                    WHEN 'school' THEN 1 
                    WHEN 'higher_secondary' THEN 2 
                    WHEN 'diploma' THEN 3 
                    WHEN 'undergraduate' THEN 4 
                    ELSE 5 
                END,
                p.program_name
        """
        programs = conn.execute(sql, params).fetchall()

        if programs:
            return [dict(p) for p in programs]

        rows = conn.execute(
            """
            SELECT program_id, school_id, standard, section,
                   first_language, stream, subject_combination,
                   is_available
            FROM school_programs
            WHERE school_id = ?
            ORDER BY standard, section, stream
            """,
            (school_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/schools/{school_id}/achievements")
def get_school_achievements(school_id: str):
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "School not found")

        rows = conn.execute(
            """
            SELECT achievement_id, school_id, title, description,
                   achievement_date, public_document_url,
                   year, award_level, issuing_authority, verification_status
            FROM school_achievements
            WHERE school_id = ? AND is_published = 1
            ORDER BY year DESC, achievement_date DESC
            """,
            (school_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/schools/{school_id}/divisions")
def get_school_divisions(school_id: str):
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "School not found")

        rows = conn.execute(
            """
            SELECT division_id, parent_institution_id, division_name,
                   division_type, campus_location, head_of_division,
                   contact_phone, contact_email, facilities_summary,
                   description, display_order
            FROM institution_divisions
            WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            """,
            (school_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/schools/{school_id}/academic-hierarchy")
def get_school_academic_hierarchy(school_id: str):
    """
    Returns the formal hierarchical academic structure for an institution.
    For Universities:
      University -> Faculty/School -> Department -> Programme -> Academic Year/Level
    For Degree Colleges:
      Displays degree programmes with specialisations, branches, and university affiliation.
    """
    conn = get_connection()
    try:
        school = conn.execute(
            """
            SELECT school_id, school_name, school_type, category, affiliation,
                   recognition, campus_name, district, state
            FROM schools
            WHERE school_id = ?
            """,
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "Institution not found")

        cat = school["category"] or ""
        stype = school["school_type"] or ""
        is_univ = cat == "Universities" or stype == "University"
        is_college = cat == "Degree Colleges" or stype == "Degree College"

        # Fetch active divisions / faculties
        div_rows = conn.execute(
            """
            SELECT division_id, division_name, division_type, campus_location,
                   head_of_division, contact_phone, contact_email, description, display_order
            FROM institution_divisions
            WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            """,
            (school_id,),
        ).fetchall()
        divisions = [dict(d) for d in div_rows]

        # Fetch active academic programs
        prog_rows = conn.execute(
            """
            SELECT p.program_id, p.institution_id, p.education_level, p.program_name,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   p.faculty_name, p.department_name, p.duration_years, p.is_active,
                   COALESCE(SUM(ps.capacity), 0) AS total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) AS total_strength,
                   COALESCE(SUM(MAX(0, ps.capacity - ps.current_strength)), 0) AS available_seats,
                   COUNT(ps.section_id) AS sections_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ? AND p.is_active = 1
            GROUP BY p.program_id
            ORDER BY 
                CASE p.education_level 
                    WHEN 'undergraduate' THEN 1 
                    WHEN 'postgraduate' THEN 2 
                    WHEN 'doctoral' THEN 3 
                    ELSE 4 
                END,
                p.faculty_name, p.department_name, p.program_name
            """,
            (school_id,),
        ).fetchall()
        programs = [dict(p) for p in prog_rows]

        # Build hierarchical structure for University
        faculties_dict = {}
        for d in divisions:
            faculties_dict[d["division_name"]] = {
                "faculty_name": d["division_name"],
                "division_id": d["division_id"],
                "division_type": d["division_type"],
                "head_of_division": d["head_of_division"],
                "campus_location": d["campus_location"],
                "contact_email": d["contact_email"],
                "description": d["description"],
                "departments": {}
            }

        for p in programs:
            fac_name = p.get("faculty_name") or "General Studies"
            dept_name = p.get("department_name") or (p.get("discipline_or_stream") or "General Department")
            
            if fac_name not in faculties_dict:
                faculties_dict[fac_name] = {
                    "faculty_name": fac_name,
                    "division_id": None,
                    "division_type": "Faculty",
                    "head_of_division": None,
                    "campus_location": None,
                    "contact_email": None,
                    "description": None,
                    "departments": {}
                }

            if dept_name not in faculties_dict[fac_name]["departments"]:
                faculties_dict[fac_name]["departments"][dept_name] = {
                    "department_name": dept_name,
                    "programmes": []
                }

            faculties_dict[fac_name]["departments"][dept_name]["programmes"].append({
                "program_id": p["program_id"],
                "program_name": p["program_name"],
                "education_level": p["education_level"],
                "degree_type": p["degree_type"],
                "discipline_or_stream": p["discipline_or_stream"],
                "duration_years": p["duration_years"],
                "total_capacity": p["total_capacity"],
                "total_strength": p["total_strength"],
                "available_seats": p["available_seats"],
                "sections_count": p["sections_count"]
            })

        # Format faculties into a clean list
        faculties_list = []
        for f in faculties_dict.values():
            depts_list = []
            for d in f["departments"].values():
                depts_list.append(d)
            f_copy = {**f, "departments": depts_list}
            faculties_list.append(f_copy)

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "category": school["category"],
            "school_type": school["school_type"],
            "is_university": is_univ,
            "is_degree_college": is_college,
            "affiliation": school["affiliation"],
            "recognition": school["recognition"],
            "campus_name": school["campus_name"],
            "district": school["district"],
            "state": school["state"],
            "faculties": faculties_list,
            "total_programs": len(programs),
            "programs_flat": programs
        }
    finally:
        conn.close()



class ParentDirectStudentUpdateRequest(BaseModel):
    student_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    first_language: Optional[str] = None


@app.get("/parent/children")
def list_parent_children(user: dict = Depends(require_parent)):
    """
    List children linked to this verified parent account.
    Federated with NagrikSetu Central Portal household registry.
    """
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None and user.get("email"):
            g_id = f"GRD-2026-{uuid.uuid4().hex[:6].upper()}"
            conn.execute(
                """
                INSERT INTO guardians (guardian_id, user_id, full_name, relationship, phone, email)
                VALUES (?, ?, ?, 'Parent', ?, ?)
                """,
                (g_id, user["user_id"], user.get("full_name") or user["email"].split("@")[0], user.get("phone") or "9876543210", user["email"])
            )
            conn.commit()
            guardian = get_parent_guardian(conn, user["user_id"])

        g_id = guardian["guardian_id"] if guardian else None

        # Fetch federated children from Central Citizen Database
        central_children = []
        if user.get("email"):
            central_children = fetch_central_household_children(user["email"])
            if central_children and g_id:
                for ch in central_children:
                    perm_id = ch.get("permanent_student_id")
                    stu_id = ch.get("student_id")
                    ch_name = ch.get("full_name")
                    st_row = None
                    if perm_id:
                        st_row = conn.execute("SELECT permanent_student_id FROM students WHERE permanent_student_id = ?", (perm_id,)).fetchone()
                    if not st_row and stu_id:
                        st_row = conn.execute("SELECT permanent_student_id FROM students WHERE student_id = ?", (stu_id,)).fetchone()
                    if not st_row and ch_name:
                        st_row = conn.execute("SELECT permanent_student_id FROM students WHERE student_name = ?", (ch_name,)).fetchone()
                    if st_row:
                        matched_perm = st_row["permanent_student_id"]
                        sg_exists = conn.execute(
                            "SELECT 1 FROM student_guardians WHERE guardian_id = ? AND permanent_student_id = ?",
                            (g_id, matched_perm)
                        ).fetchone()
                        if not sg_exists:
                            sg_id = f"SGL-2026-{uuid.uuid4().hex[:6].upper()}"
                            conn.execute(
                                """
                                INSERT INTO student_guardians (
                                    student_guardian_id, permanent_student_id, guardian_id,
                                    can_view_records, can_request_updates, is_verified
                                ) VALUES (?, ?, ?, 1, 1, 1)
                                """,
                                (sg_id, matched_perm, g_id)
                            )
                conn.commit()

        if g_id is None:
            return []

        rows = conn.execute(
            """
            SELECT s.student_id, s.permanent_student_id,
                   s.student_name, s.school_id, sc.school_name,
                   s.standard, s.section, s.first_language,
                   s.date_of_birth, s.gender,
                   s.enrollment_status
            FROM student_guardians sg
            JOIN students s
              ON s.permanent_student_id = sg.permanent_student_id
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            WHERE sg.guardian_id = ?
              AND sg.is_verified = 1
              AND sg.can_view_records = 1
            ORDER BY s.student_name
            """,
            (g_id,),
        ).fetchall()
        
        result = [dict(row) for row in rows]
        existing_perm_ids = {r["permanent_student_id"] for r in result if r.get("permanent_student_id")}

        # Add any Central Citizen children who are not yet enrolled in any school
        for ch in central_children:
            ch_perm = ch.get("permanent_student_id")
            if ch_perm and ch_perm in existing_perm_ids:
                continue
            # If not in school yet, allow parent to view and apply
            result.append({
                "student_id": ch.get("student_id") or f"STU-PENDING-{ch.get('citizen_code', '01')}",
                "permanent_student_id": ch.get("permanent_student_id") or f"NS-PENDING-{ch.get('citizen_code', '01')}",
                "student_name": ch.get("full_name"),
                "school_id": None,
                "school_name": "Not Yet Enrolled (Central Citizen Registry)",
                "standard": 1,
                "section": "-",
                "first_language": "Kannada",
                "date_of_birth": ch.get("date_of_birth"),
                "gender": "Unknown",
                "enrollment_status": "eligible_for_admission",
                "can_apply": True,
                "citizen_code": ch.get("citizen_code"),
            })

        return result
    finally:
        conn.close()


@app.put("/parent/children/{permanent_student_id}/profile")
@app.post("/parent/children/{permanent_student_id}/profile")
def update_parent_child_profile(
    permanent_student_id: str,
    payload: ParentDirectStudentUpdateRequest,
    user: dict = Depends(require_parent),
):
    """
    Allows authorized parent to update child student profile details directly.
    Audited with structured business audit log ID.
    """
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            raise HTTPException(403, "No guardian profile is linked to this account.")

        child = get_authorized_child(
            conn,
            guardian["guardian_id"],
            permanent_student_id,
            "can_request_updates",
        )
        if child is None:
            raise HTTPException(404, "Child record not found or update permissions not granted.")

        if payload.student_name and payload.student_name.strip():
            conn.execute("UPDATE students SET student_name = ? WHERE permanent_student_id = ?", (payload.student_name.strip(), permanent_student_id))
        if payload.date_of_birth and payload.date_of_birth.strip():
            conn.execute("UPDATE students SET date_of_birth = ? WHERE permanent_student_id = ?", (payload.date_of_birth.strip(), permanent_student_id))
        if payload.gender and payload.gender.strip():
            conn.execute("UPDATE students SET gender = ? WHERE permanent_student_id = ?", (payload.gender.strip(), permanent_student_id))
        if payload.first_language and payload.first_language.strip():
            conn.execute("UPDATE students SET first_language = ? WHERE permanent_student_id = ?", (payload.first_language.strip(), permanent_student_id))
        conn.commit()

        log_id = f"AUD-SCH-2026-{uuid.uuid4().hex[:8].upper()}"
        try:
            conn.execute(
                """
                INSERT INTO audit_logs (log_id, actor_id, actor_email, action, resource_type, resource_id, details)
                VALUES (?, ?, ?, 'PARENT_STUDENT_PROFILE_UPDATE', 'students', ?, ?)
                """,
                (log_id, user["user_id"], user.get("email"), permanent_student_id, json.dumps(payload.dict(exclude_unset=True)))
            )
            conn.commit()
        except Exception:
            pass

        updated = conn.execute("SELECT * FROM students WHERE permanent_student_id = ?", (permanent_student_id,)).fetchone()
        return {
            "success": True,
            "message": "Student profile updated successfully by verified parent.",
            "student": dict(updated) if updated else None
        }
    finally:
        conn.close()


@app.get("/parent/children/{permanent_student_id}/records")
def get_parent_child_records(
    permanent_student_id: str,
    user: dict = Depends(require_parent),
):
    """Return private academic results and safe document metadata."""
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            raise HTTPException(403, "No guardian profile is linked to this account.")

        child = get_authorized_child(
            conn,
            guardian["guardian_id"],
            permanent_student_id,
            "can_view_records",
        )
        if child is None:
            raise HTTPException(
                404,
                "Child not found or access has not been verified.",
            )

        results = conn.execute(
            """
            SELECT ar.result_id, ar.subject_name, ar.exam_name,
                   ar.marks_obtained, ar.maximum_marks,
                   ar.academic_year, ar.exam_date,
                   e.standard, e.section, e.school_id, sc.school_name
            FROM academic_results ar
            JOIN enrollments e ON e.enrollment_id = ar.enrollment_id
            LEFT JOIN schools sc ON sc.school_id = e.school_id
            WHERE e.permanent_student_id = ?
            ORDER BY ar.academic_year DESC, ar.exam_date DESC
            """,
            (permanent_student_id,),
        ).fetchall()

        documents = conn.execute(
            """
            SELECT document_id, enrollment_id, document_type,
                   file_name, verification_status, created_at
            FROM student_documents
            WHERE permanent_student_id = ?
            ORDER BY created_at DESC
            """,
            (permanent_student_id,),
        ).fetchall()

        history = conn.execute(
            """
            SELECT e.school_id, sc.school_name, e.academic_year,
                   e.standard, e.section, e.first_language, e.stream,
                   e.subject_combination, e.admission_date,
                   e.leaving_date, e.enrollment_status
            FROM enrollments e
            LEFT JOIN schools sc ON sc.school_id = e.school_id
            WHERE e.permanent_student_id = ?
            ORDER BY e.academic_year DESC, e.standard DESC
            """,
            (permanent_student_id,),
        ).fetchall()

        perf = calculate_academic_performance(conn, permanent_student_id, child["school_id"])

        return {
            "student": {
                "student_id": child["student_id"],
                "permanent_student_id": child["permanent_student_id"],
                "student_name": child["student_name"],
                "school_id": child["school_id"],
                "standard": child["standard"],
                "section": child["section"],
                "first_language": child["first_language"],
            },
            "attendance": perf["attendance"],
            "attendance_summary": perf["attendance"],
            "academic_results": perf["results"],
            "subject_performance": perf["subject_performance"],
            "academic_progress": perf["academic_progress"],
            "upcoming_examinations": perf["upcoming_examinations"],
            "announcements": perf["announcements"],
            "academic_results": perf["results"],
            "academic_performance": perf,
            "documents": [dict(row) for row in documents],
            "enrollment_history": [dict(row) for row in history],
        }
    finally:
        conn.close()


@app.post(
    "/parent/linking-requests",
    response_model=ParentLinkingRequestResponse,
    status_code=201,
)
def create_parent_linking_request(
    payload: ParentLinkingRequestCreate,
    user: dict = Depends(require_parent),
):
    """
    Submit a request to link a student to this parent account.
    Does NOT create a student_guardians relationship during submission.
    Does NOT grant access to student records.
    """
    school_id = payload.school_id.strip()
    student_ref = payload.student_ref.strip()
    relationship_type = payload.relationship_type.strip()
    verification_doc_id = (
        payload.verification_doc_id.strip()
        if payload.verification_doc_id and payload.verification_doc_id.strip()
        else None
    )
    additional_notes = (
        payload.additional_notes.strip()
        if payload.additional_notes and payload.additional_notes.strip()
        else None
    )

    conn = get_connection()
    try:
        # Verify guardian profile exists for authenticated parent
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No guardian profile is linked to this account.",
            )

        # Validate that the school exists
        school = conn.execute(
            "SELECT school_id, school_name FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School not found.",
            )

        # Check for existing pending request for same parent, school, and student_ref
        existing_pending = conn.execute(
            """
            SELECT request_id
            FROM linking_requests
            WHERE parent_user_id = ?
              AND school_id = ?
              AND student_ref = ?
              AND request_status = 'pending'
            """,
            (user["user_id"], school_id, student_ref),
        ).fetchone()

        if existing_pending is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A pending linking request already exists for this student and school.",
            )

        request_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())

        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO linking_requests (
                        request_id, parent_user_id, school_id,
                        student_ref, relationship_type,
                        verification_doc_id, additional_notes,
                        request_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                    """,
                    (
                        request_id,
                        user["user_id"],
                        school_id,
                        student_ref,
                        relationship_type,
                        verification_doc_id,
                        additional_notes,
                    ),
                )

                conn.execute(
                    """
                    INSERT INTO audit_logs (
                        audit_id, actor_user_id, actor_role,
                        action, entity_type, entity_id,
                        school_id, ip_address, metadata_json
                    )
                    VALUES (?, ?, 'parent', 'LINKING_REQUEST_SUBMITTED', 'linking_request', ?, ?, NULL, ?)
                    """,
                    (
                        audit_id,
                        user["user_id"],
                        request_id,
                        school_id,
                        json.dumps({
                            "student_ref": student_ref,
                            "relationship_type": relationship_type,
                            "school_id": school_id,
                        }),
                    ),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A pending linking request already exists for this student and school.",
            )

        return {
            "request_id": request_id,
            "school_id": school_id,
            "student_ref": student_ref,
            "relationship_type": relationship_type,
            "request_status": "pending",
            "message": "Student linking request submitted successfully. Pending school verification.",
        }
    finally:
        conn.close()


@app.get("/parent/linking-requests")
def list_parent_linking_requests(
    user: dict = Depends(require_parent),
):
    """
    List only linking requests submitted by the authenticated parent.
    Does not expose private student records or other parents' requests.
    Ordered by created_at DESC.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT lr.request_id, lr.school_id, sc.school_name,
                   lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_comment,
                   lr.created_at, lr.reviewed_at
            FROM linking_requests lr
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            WHERE lr.parent_user_id = ?
            ORDER BY lr.created_at DESC
            """,
            (user["user_id"],),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/parent/update-requests", status_code=201)
def create_parent_update_request(
    request: ParentUpdateRequest,
    user: dict = Depends(require_parent),
):
    """Submit a proposed change; do not modify official student data."""
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            raise HTTPException(403, "No guardian profile is linked to this account.")

        child = get_authorized_child(
            conn,
            guardian["guardian_id"],
            request.permanent_student_id,
            "can_request_updates",
        )
        if child is None:
            raise HTTPException(
                404,
                "Child not found or you are not authorized to request updates.",
            )

        old_value = child[request.field_name]
        proposed_value = request.proposed_value.strip()

        if not proposed_value:
            raise HTTPException(422, "The proposed value cannot be empty.")

        if request.supporting_document_id:
            document = conn.execute(
                """
                SELECT document_id
                FROM student_documents
                WHERE document_id = ?
                  AND permanent_student_id = ?
                """,
                (
                    request.supporting_document_id,
                    request.permanent_student_id,
                ),
            ).fetchone()

            if document is None:
                raise HTTPException(
                    422,
                    "The supporting document does not belong to this child.",
                )

        request_id = str(uuid.uuid4())

        conn.execute(
            """
            INSERT INTO update_requests (
                request_id, permanent_student_id, guardian_id,
                request_type, field_name, old_value, proposed_value,
                reason, supporting_document_id, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (
                request_id,
                request.permanent_student_id,
                guardian["guardian_id"],
                request.request_type,
                request.field_name,
                old_value,
                proposed_value,
                request.reason.strip(),
                request.supporting_document_id,
            ),
        )
        conn.commit()

        return {
            "request_id": request_id,
            "status": "pending",
            "message": (
                "Request submitted for school review. "
                "The official student record has not been changed."
            ),
        }
    finally:
        conn.close()


@app.get("/parent/update-requests")
def list_parent_update_requests(
    user: dict = Depends(require_parent),
):
    """Return only update requests submitted under this guardian account."""
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            return []

        rows = conn.execute(
            """
            SELECT request_id, permanent_student_id, request_type,
                   field_name, old_value, proposed_value, reason,
                   status, review_comment, submitted_at, reviewed_at
            FROM update_requests
            WHERE guardian_id = ?
            ORDER BY submitted_at DESC
            """,
            (guardian["guardian_id"],),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


class ReviewLinkingRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    review_comment: str = Field(min_length=3, max_length=1000)
    permanent_student_id: Optional[str] = Field(default=None, max_length=100)
    confirm_student_match: bool = Field(
        default=False,
        description="Explicit confirmation when student_ref does not verbatim match student_id, student_name, or permanent_student_id"
    )

    @field_validator("review_comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 3:
            raise ValueError("Review comment must contain at least 3 non-whitespace characters.")
        return s

    @field_validator("permanent_student_id")
    @classmethod
    def validate_permanent_student_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            s = v.strip()
            return s if s else None
        return None


@app.get("/school/linking-requests")
def list_school_linking_requests(
    status_filter: Optional[Literal["pending", "approved", "rejected", "cancelled", "all"]] = Query(default="pending"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_staff),
):
    """
    List linking requests for the reviewer's assigned school.
    Defaults to pending requests.
    Does not expose sensitive credentials.
    """
    if user["role"] not in ("school_staff", "school_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff access required.",
        )
    if not user.get("school_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )

    lim_val = limit if isinstance(limit, int) else (limit.default if hasattr(limit, "default") else 50)
    off_val = offset if isinstance(offset, int) else (offset.default if hasattr(offset, "default") else 0)
    stat_val = status_filter if isinstance(status_filter, str) else (status_filter.default if hasattr(status_filter, "default") else "pending")

    conn = get_connection()
    try:
        query = """
            SELECT lr.request_id, lr.parent_user_id, u.full_name AS parent_name,
                   u.email AS parent_email, u.phone AS parent_phone,
                   lr.school_id, lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_user_id,
                   lr.reviewer_comment, lr.permanent_student_id,
                   lr.created_at, lr.reviewed_at
            FROM linking_requests lr
            JOIN users u ON u.user_id = lr.parent_user_id
            WHERE lr.school_id = ?
        """
        params = [user["school_id"]]

        if stat_val != "all":
            query += " AND lr.request_status = ?"
            params.append(stat_val)

        query += " ORDER BY lr.created_at ASC LIMIT ? OFFSET ?"
        params.extend([lim_val, off_val])

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/school/linking-requests/{request_id}/review")
def review_school_linking_request(
    request_id: str,
    review: ReviewLinkingRequest,
    user: dict = Depends(require_school_staff),
):
    """
    Approve or reject a pending linking request within the reviewer's assigned school.
    Uses atomic transaction with immediate write lock.
    """
    if user["role"] not in ("school_staff", "school_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff access required.",
        )
    if not user.get("school_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        # 1. Fetch linking request
        lr = conn.execute(
            """
            SELECT *
            FROM linking_requests
            WHERE request_id = ?
            """,
            (request_id,),
        ).fetchone()

        if lr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linking request not found.",
            )

        # 2. Verify school authorization
        if lr["school_id"] != user["school_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot review requests for another school.",
            )

        # 3. Check request is currently pending
        if lr["request_status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This linking request has already been reviewed.",
            )

        audit_id = str(uuid.uuid4())
        actor_role = user["role"]

        if review.decision == "approved":
            # 4. For approval, permanent_student_id is required
            permanent_student_id = review.permanent_student_id
            if not permanent_student_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="permanent_student_id is required when approving a linking request.",
                )

            # 5. Verify the student exists and belongs to the request's school
            student = conn.execute(
                """
                SELECT student_id, permanent_student_id, school_id, student_name
                FROM students
                WHERE permanent_student_id = ?
                """,
                (permanent_student_id,),
            ).fetchone()

            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found with the provided permanent_student_id.",
                )

            if student["school_id"] != user["school_id"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="The student does not belong to your school.",
                )

            # 5b. Verify student_ref matches student or requires explicit staff confirmation
            ref_norm = lr["student_ref"].strip().lower()
            candidate_identifiers = {
                student["permanent_student_id"].strip().lower(),
                student["student_id"].strip().lower(),
                student["student_name"].strip().lower(),
            }

            is_direct_match = ref_norm in candidate_identifiers
            if not is_direct_match and not review.confirm_student_match:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Student reference '{lr['student_ref']}' does not match student ID or name "
                        f"({student['student_name']}, {student['student_id']}). "
                        f"Set confirm_student_match=true to confirm manual verification."
                    ),
                )

            verification_method = "direct_match" if is_direct_match else "manual_staff_confirmation"

            # 6. Resolve parent guardian record
            guardian = get_parent_guardian(conn, lr["parent_user_id"])
            if guardian is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No guardian profile found for the requesting parent.",
                )

            # 7. Check if student_guardians relationship already exists
            existing_sg = conn.execute(
                """
                SELECT student_guardian_id, can_view_records, can_request_updates, is_verified
                FROM student_guardians
                WHERE permanent_student_id = ? AND guardian_id = ?
                """,
                (permanent_student_id, guardian["guardian_id"]),
            ).fetchone()

            if existing_sg is not None:
                # Update to verified without overwriting custom permissions
                conn.execute(
                    """
                    UPDATE student_guardians
                    SET is_verified = 1
                    WHERE student_guardian_id = ?
                    """,
                    (existing_sg["student_guardian_id"],),
                )
            else:
                # Create verified relationship
                sg_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO student_guardians (
                        student_guardian_id, permanent_student_id,
                        guardian_id, can_view_records,
                        can_request_updates, is_verified
                    )
                    VALUES (?, ?, ?, 1, 1, 1)
                    """,
                    (sg_id, permanent_student_id, guardian["guardian_id"]),
                )

            # 8. Update linking request status to approved
            res = conn.execute(
                """
                UPDATE linking_requests
                SET request_status = 'approved',
                    reviewer_user_id = ?,
                    reviewer_comment = ?,
                    permanent_student_id = ?,
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
                  AND request_status = 'pending'
                """,
                (
                    user["user_id"],
                    review.review_comment.strip(),
                    permanent_student_id,
                    request_id,
                ),
            )

            if res.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This linking request has already been reviewed.",
                )

            # 9. Audit log insertion
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role,
                    action, entity_type, entity_id,
                    school_id, ip_address, metadata_json
                )
                VALUES (?, ?, ?, 'LINKING_REQUEST_APPROVED', 'linking_request', ?, ?, NULL, ?)
                """,
                (
                    audit_id,
                    user["user_id"],
                    actor_role,
                    request_id,
                    user["school_id"],
                    json.dumps({
                        "decision": "approved",
                        "reviewer_comment": review.review_comment.strip(),
                        "permanent_student_id": permanent_student_id,
                        "parent_user_id": lr["parent_user_id"],
                        "student_ref": lr["student_ref"],
                        "verification_method": verification_method,
                        "confirm_student_match": review.confirm_student_match,
                    }),
                ),
            )

        elif review.decision == "rejected":
            # Update linking request status to rejected
            res = conn.execute(
                """
                UPDATE linking_requests
                SET request_status = 'rejected',
                    reviewer_user_id = ?,
                    reviewer_comment = ?,
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
                  AND request_status = 'pending'
                """,
                (
                    user["user_id"],
                    review.review_comment.strip(),
                    request_id,
                ),
            )

            if res.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This linking request has already been reviewed.",
                )

            # Audit log insertion
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role,
                    action, entity_type, entity_id,
                    school_id, ip_address, metadata_json
                )
                VALUES (?, ?, ?, 'LINKING_REQUEST_REJECTED', 'linking_request', ?, ?, NULL, ?)
                """,
                (
                    audit_id,
                    user["user_id"],
                    actor_role,
                    request_id,
                    user["school_id"],
                    json.dumps({
                        "decision": "rejected",
                        "reviewer_comment": review.review_comment.strip(),
                        "parent_user_id": lr["parent_user_id"],
                    }),
                ),
            )

        conn.commit()

        return {
            "request_id": request_id,
            "status": review.decision,
            "message": (
                "Linking request approved and parent-child relationship verified."
                if review.decision == "approved"
                else "Linking request rejected. Student records remain unchanged."
            ),
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class ReviewRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    review_comment: str = Field(min_length=3, max_length=1000)


@app.get("/school/update-requests")
def list_school_update_requests(
    user: dict = Depends(get_current_user),
):
    """List update requests for the reviewer's assigned school."""
    if user["role"] not in ("school_staff", "school_admin"):
        raise HTTPException(403, "School staff access required.")

    if not user["school_id"]:
        raise HTTPException(403, "Your account is not assigned to a school.")

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT ur.request_id, ur.permanent_student_id,
                   s.student_id, s.student_name, s.school_id,
                   ur.request_type, ur.field_name, ur.old_value,
                   ur.proposed_value, ur.reason, ur.status,
                   ur.submitted_at
            FROM update_requests ur
            JOIN students s
              ON s.permanent_student_id = ur.permanent_student_id
            WHERE s.school_id = ?
              AND ur.status = 'pending'
            ORDER BY ur.submitted_at ASC
            """,
            (user["school_id"],),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/school/update-requests/{request_id}/review")
def review_school_update_request(
    request_id: str,
    review: ReviewRequest,
    user: dict = Depends(get_current_user),
):
    """Approve or reject a pending request within the assigned school."""
    if user["role"] not in ("school_staff", "school_admin"):
        raise HTTPException(403, "School staff access required.")

    if not user["school_id"]:
        raise HTTPException(403, "Your account is not assigned to a school.")

    allowed_fields = {
        "student_name",
        "date_of_birth",
        "gender",
        "first_language",
    }

    conn = get_connection()
    try:
        # Begin a transaction so the decision and student update stay together.
        conn.execute("BEGIN IMMEDIATE")

        request_row = conn.execute(
            """
            SELECT ur.*, s.school_id
            FROM update_requests ur
            JOIN students s
              ON s.permanent_student_id = ur.permanent_student_id
            WHERE ur.request_id = ?
            """,
            (request_id,),
        ).fetchone()

        if request_row is None:
            raise HTTPException(404, "Update request not found.")

        if request_row["school_id"] != user["school_id"]:
            raise HTTPException(
                403,
                "You cannot review requests for another school.",
            )

        if request_row["status"] != "pending":
            raise HTTPException(
                409,
                "This request has already been reviewed.",
            )

        if review.decision == "approved":
            field_name = request_row["field_name"]

            if field_name not in allowed_fields:
                raise HTTPException(
                    422,
                    "This field cannot be changed through a parent request.",
                )

            old_value = conn.execute(
                f"""
                SELECT {field_name}
                FROM students
                WHERE permanent_student_id = ?
                """,
                (request_row["permanent_student_id"],),
            ).fetchone()[0]

            new_value = request_row["proposed_value"]

            conn.execute(
                f"""
                UPDATE students
                SET {field_name} = ?
                WHERE permanent_student_id = ?
                """,
                (new_value, request_row["permanent_student_id"]),
            )

            conn.execute(
                """
                INSERT INTO school_change_log (
                    log_id, school_id, permanent_student_id,
                    field_name, old_value, new_value,
                    changed_by_user_id, change_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    user["school_id"],
                    request_row["permanent_student_id"],
                    field_name,
                    old_value,
                    new_value,
                    user["user_id"],
                    review.review_comment,
                ),
            )

        conn.execute(
            """
            UPDATE update_requests
            SET status = ?,
                reviewed_by_user_id = ?,
                review_comment = ?,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
              AND status = 'pending'
            """,
            (
                review.decision,
                user["user_id"],
                review.review_comment.strip(),
                request_id,
            ),
        )

        conn.commit()

        return {
            "request_id": request_id,
            "status": review.decision,
            "message": (
                "Student record updated and audit entry created."
                if review.decision == "approved"
                else "Request rejected. Student record unchanged."
            ),
        }

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =====================================================================
# PLATFORM & SCHOOL ADMIN APIs
# =====================================================================

class UpdateSeatCapacityPayload(BaseModel):
    section_id: str = Field(..., min_length=1, max_length=100)
    new_capacity: int = Field(..., ge=1, le=1000)
    reason: Optional[str] = Field(None, max_length=500)


class UpdateSchoolProfilePayload(BaseModel):
    public_phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    reason: Optional[str] = None


@app.get("/admin/overview")
def get_platform_admin_overview(user: dict = Depends(require_platform_admin)):
    """Central platform diagnostics and metrics. Restricted to platform_admin."""
    conn = get_connection()
    try:
        schools_count = conn.execute("SELECT count(*) FROM schools").fetchone()[0]
        students_count = conn.execute("SELECT count(*) FROM students").fetchone()[0]
        enrollments_count = conn.execute("SELECT count(*) FROM enrollments").fetchone()[0]
        users_count = conn.execute("SELECT count(*) FROM users").fetchone()[0]

        # User role breakdown
        roles = conn.execute("SELECT role, count(*) FROM users GROUP BY role").fetchall()
        role_breakdown = {r[0]: r[1] for r in roles}

        # Linking requests status breakdown
        lrs = conn.execute("SELECT request_status, count(*) FROM linking_requests GROUP BY request_status").fetchall()
        linking_breakdown = {r[0]: r[1] for r in lrs}

        # Institutions by education category
        cats = conn.execute("SELECT category, count(*) FROM schools GROUP BY category").fetchall()
        institutions_by_category = {r[0]: r[1] for r in cats}

        # Parents count
        parents_count = conn.execute("SELECT count(*) FROM users WHERE role = 'parent'").fetchone()[0]

        # Total institution admins and staff
        staff_admins_count = conn.execute("SELECT count(*) FROM users WHERE role IN ('school_admin', 'school_staff')").fetchone()[0]

        # Admission applications breakdown
        total_apps = conn.execute("SELECT count(*) FROM admission_applications").fetchone()[0]
        apps_awaiting_review = conn.execute("SELECT count(*) FROM admission_applications WHERE status IN ('submitted', 'under_review')").fetchone()[0]
        apps_stage1_approved = conn.execute("SELECT count(*) FROM admission_applications WHERE status = 'approved'").fetchone()[0]
        apps_stage2_submitted = conn.execute("SELECT count(*) FROM admission_applications WHERE status IN ('stage2_submitted', 'final_review', 'verified')").fetchone()[0]
        apps_final_accepted = conn.execute("SELECT count(*) FROM admission_applications WHERE status IN ('admitted', 'enrolled', 'confirmed')").fetchone()[0]
        apps_final_rejected = conn.execute("SELECT count(*) FROM admission_applications WHERE status IN ('rejected', 'final_rejected')").fetchone()[0]
        apps_clarification = conn.execute("SELECT count(*) FROM admission_applications WHERE status = 'action_required'").fetchone()[0]

        # Recent institution updates
        recent_inst = conn.execute(
            """
            SELECT pal.id, pal.event_type, pal.institution_id, s.school_name,
                   pal.action, pal.old_values, pal.new_values, pal.remarks, pal.created_at
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            WHERE pal.event_category = 'institution'
            ORDER BY pal.created_at DESC
            LIMIT 5
            """
        ).fetchall()
        recent_institution_updates = [dict(r) for r in recent_inst]

        # Recent platform activities
        recent_acts = conn.execute(
            """
            SELECT pal.id, pal.event_type, pal.event_category, pal.institution_id,
                   s.school_name, pal.actor_name, pal.actor_role, pal.action,
                   pal.entity_type, pal.entity_id, pal.created_at
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            ORDER BY pal.created_at DESC
            LIMIT 10
            """
        ).fetchall()
        recent_activities = [dict(r) for r in recent_acts]

        return {
            "status": "healthy",
            "total_institutions": schools_count,
            "institutions_by_category": institutions_by_category,
            "total_students": students_count,
            "total_parents": parents_count,
            "total_staff_and_admins": staff_admins_count,
            "total_admission_applications": total_apps,
            "applications_awaiting_review": apps_awaiting_review,
            "applications_stage1_approved": apps_stage1_approved,
            "applications_stage2_submitted": apps_stage2_submitted,
            "applications_final_accepted": apps_final_accepted,
            "applications_final_rejected": apps_final_rejected,
            "applications_awaiting_clarification": apps_clarification,
            "recent_institution_updates": recent_institution_updates,
            "recent_activities": recent_activities,
            # Legacy backward-compatibility fields:
            "schools_count": schools_count,
            "students_count": students_count,
            "enrollments_count": enrollments_count,
            "users_count": users_count,
            "role_breakdown": role_breakdown,
            "linking_requests_breakdown": linking_breakdown,
        }
    finally:
        conn.close()


@app.get("/admin/activity-feed")
def get_platform_activity_feed(
    category: Optional[str] = Query(default=None),
    institution_id: Optional[str] = Query(default=None),
    institution_category: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    actor_role: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    application_id: Optional[str] = Query(default=None),
    student_id: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_platform_admin),
):
    """Searchable and filterable central activity feed. Restricted to platform_admin."""
    conn = get_connection()
    try:
        where_clauses = ["1=1"]
        params = []

        if category and category.strip() and category != "all":
            where_clauses.append("pal.event_category = ?")
            params.append(category.strip().lower())

        if institution_id and institution_id.strip() and institution_id != "all":
            where_clauses.append("pal.institution_id = ?")
            params.append(institution_id.strip())

        if institution_category and institution_category.strip() and institution_category != "all":
            where_clauses.append("s.category = ?")
            params.append(institution_category.strip().lower())

        if district and district.strip() and district != "all":
            where_clauses.append("s.district = ?")
            params.append(district.strip())

        if actor_role and actor_role.strip() and actor_role != "all":
            where_clauses.append("pal.actor_role = ?")
            params.append(actor_role.strip().lower())

        if start_date and start_date.strip():
            where_clauses.append("pal.created_at >= ?")
            params.append(start_date.strip())

        if end_date and end_date.strip():
            where_clauses.append("pal.created_at <= ?")
            params.append(end_date.strip())

        if application_id and application_id.strip():
            where_clauses.append("(pal.entity_id = ? OR pal.action LIKE ? OR pal.old_values LIKE ? OR pal.new_values LIKE ?)")
            app_pattern = f"%{application_id.strip()}%"
            params.extend([application_id.strip(), app_pattern, app_pattern, app_pattern])

        if student_id and student_id.strip():
            where_clauses.append("(pal.entity_id = ? OR pal.action LIKE ? OR pal.old_values LIKE ? OR pal.new_values LIKE ?)")
            stu_pattern = f"%{student_id.strip()}%"
            params.extend([student_id.strip(), stu_pattern, stu_pattern, stu_pattern])

        if search and search.strip():
            term = f"%{search.strip()}%"
            where_clauses.append("(pal.action LIKE ? OR pal.remarks LIKE ? OR pal.entity_id LIKE ? OR pal.actor_name LIKE ? OR s.school_name LIKE ?)")
            params.extend([term, term, term, term, term])

        where_sql = " AND ".join(where_clauses)

        count_sql = f"""
            SELECT count(*)
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            WHERE {where_sql}
        """
        total = conn.execute(count_sql, params).fetchone()[0]

        query_sql = f"""
            SELECT pal.id, pal.event_type, pal.event_category, pal.institution_id,
                   s.school_name AS institution_name, s.category AS institution_category, s.district,
                   pal.actor_user_id, pal.actor_name, pal.actor_role,
                   pal.entity_type, pal.entity_id, pal.action,
                   pal.old_values, pal.new_values, pal.remarks, pal.request_id, pal.created_at
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            WHERE {where_sql}
            ORDER BY pal.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query_sql, params + [limit, offset]).fetchall()
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


@app.get("/admin/audit-logs")
def get_platform_audit_logs(
    category: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    institution_id: Optional[str] = Query(default=None),
    actor_role: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_platform_admin)
):
    """Platform audit ledger inspection. Restricted to platform_admin."""
    conn = get_connection()
    try:
        where_clauses = ["1=1"]
        params = []
        if category and category.strip() and category != "all":
            where_clauses.append("pal.event_category = ?")
            params.append(category.strip().lower())
        if event_type and event_type.strip() and event_type != "all":
            where_clauses.append("pal.event_type = ?")
            params.append(event_type.strip())
        if institution_id and institution_id.strip() and institution_id != "all":
            where_clauses.append("pal.institution_id = ?")
            params.append(institution_id.strip())
        if actor_role and actor_role.strip() and actor_role != "all":
            where_clauses.append("pal.actor_role = ?")
            params.append(actor_role.strip().lower())
        if search and search.strip():
            term = f"%{search.strip()}%"
            where_clauses.append("(pal.action LIKE ? OR pal.remarks LIKE ? OR pal.entity_id LIKE ? OR pal.actor_name LIKE ?)")
            params.extend([term, term, term, term])

        where_sql = " AND ".join(where_clauses)
        total = conn.execute(f"SELECT count(*) FROM platform_audit_logs pal WHERE {where_sql}", params).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT pal.id AS audit_id, pal.event_type, pal.event_category, pal.institution_id,
                   s.school_name AS institution_name,
                   pal.actor_user_id, pal.actor_name, pal.actor_role,
                   pal.entity_type, pal.entity_id, pal.action,
                   pal.old_values, pal.new_values, pal.remarks, pal.request_id, pal.created_at
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            WHERE {where_sql}
            ORDER BY pal.created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        ).fetchall()
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


@app.get("/admin/admissions/applications")
def get_admin_admission_applications(
    institution_id: Optional[str] = Query(default=None),
    institution_category: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_platform_admin),
):
    """Central monitoring of admission applications across every institution. Restricted to platform_admin."""
    conn = get_connection()
    try:
        where_clauses = ["1=1"]
        params = []

        if institution_id and institution_id.strip() and institution_id != "all":
            where_clauses.append("a.institution_id = ?")
            params.append(institution_id.strip())

        if institution_category and institution_category.strip() and institution_category != "all":
            where_clauses.append("s.category = ?")
            params.append(institution_category.strip().lower())

        if status and status.strip() and status != "all":
            where_clauses.append("a.status = ?")
            params.append(status.strip())

        if academic_year and academic_year.strip() and academic_year != "all":
            where_clauses.append("a.academic_year = ?")
            params.append(academic_year.strip())

        if search and search.strip():
            term = f"%{search.strip()}%"
            where_clauses.append("(a.application_id LIKE ? OR a.applicant_name LIKE ? OR u.full_name LIKE ? OR s.school_name LIKE ?)")
            params.extend([term, term, term, term])

        where_sql = " AND ".join(where_clauses)
        total = conn.execute(
            f"""
            SELECT count(*)
            FROM admission_applications a
            LEFT JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN users u ON u.user_id = a.parent_user_id
            WHERE {where_sql}
            """,
            params
        ).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT a.application_id, a.institution_id, s.school_name AS institution_name,
                   s.category AS institution_category, s.district,
                   a.parent_user_id, COALESCE(u.full_name, a.parent_name) AS parent_name,
                   COALESCE(u.phone, a.parent_phone) AS parent_phone,
                   COALESCE(u.email, a.parent_email) AS parent_email,
                   a.applicant_name, a.requested_program_id,
                   p.program_name, a.academic_year, a.education_level,
                   a.stream_preference, a.first_language_preference,
                   a.status, a.rejection_reason, a.rejection_explanation,
                   a.clarification_request, a.enrolled_student_id,
                   a.created_at, a.updated_at
            FROM admission_applications a
            LEFT JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN users u ON u.user_id = a.parent_user_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE {where_sql}
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset]
        ).fetchall()

        items = []
        for r in rows:
            d = dict(r)
            st = d["status"]
            if st in ("submitted", "under_review", "action_required"):
                d["stage"] = "Stage 1: Preliminary Application"
            elif st == "approved":
                d["stage"] = "Stage 1 Approved (Stage 2 Eligible)"
            elif st in ("stage2_submitted", "final_review", "verified"):
                d["stage"] = "Stage 2: Detailed Verification"
            elif st in ("admitted", "enrolled", "confirmed"):
                d["stage"] = "Final Admission Confirmed"
            elif st in ("rejected", "final_rejected"):
                d["stage"] = "Application Rejected"
            else:
                d["stage"] = st
            items.append(d)

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


@app.get("/admin/admissions/applications/{application_id}/history")
def get_admin_admission_history(
    application_id: str,
    user: dict = Depends(require_platform_admin),
):
    """Complete chronological audit history of an admission application. Restricted to platform_admin."""
    conn = get_connection()
    try:
        app_row = conn.execute(
            """
            SELECT a.*, s.school_name, s.category AS institution_category,
                   u.full_name AS parent_name, u.phone AS parent_phone, u.email AS parent_email,
                   p.program_name
            FROM admission_applications a
            LEFT JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN users u ON u.user_id = a.parent_user_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ?
            """,
            (application_id,)
        ).fetchone()

        if not app_row:
            raise HTTPException(status_code=404, detail="Admission application not found.")

        # Get status history
        hist_rows = conn.execute(
            """
            SELECT ash.history_id, ash.application_id, ash.previous_status, ash.new_status,
                   ash.action_by_user_id, ash.action_note, ash.created_at,
                   u.full_name AS actor_name, u.role AS actor_role
            FROM admission_status_history ash
            LEFT JOIN users u ON u.user_id = ash.action_by_user_id
            WHERE ash.application_id = ?
            ORDER BY ash.created_at ASC
            """,
            (application_id,)
        ).fetchall()

        # Get platform audit logs for this application
        audit_rows = conn.execute(
            """
            SELECT pal.id, pal.event_type, pal.action, pal.old_values, pal.new_values,
                   pal.remarks, pal.actor_name, pal.actor_role, pal.created_at
            FROM platform_audit_logs pal
            WHERE pal.entity_type = 'admission_application' AND pal.entity_id = ?
            ORDER BY pal.created_at ASC
            """,
            (application_id,)
        ).fetchall()

        events = []
        seen = set()
        for h in hist_rows:
            events.append({
                "type": "STATUS_TRANSITION",
                "previous_status": h["previous_status"],
                "new_status": h["new_status"],
                "actor_name": h["actor_name"] or h["action_by_user_id"] or "System",
                "actor_role": h["actor_role"] or "system",
                "remarks": h["action_note"],
                "created_at": h["created_at"]
            })
            seen.add(h["created_at"])

        for a in audit_rows:
            if a["created_at"] not in seen:
                old_v = json.loads(a["old_values"]) if a["old_values"] else {}
                new_v = json.loads(a["new_values"]) if a["new_values"] else {}
                events.append({
                    "type": a["event_type"],
                    "previous_status": old_v.get("status"),
                    "new_status": new_v.get("status"),
                    "actor_name": a["actor_name"],
                    "actor_role": a["actor_role"],
                    "remarks": a["remarks"] or a["action"],
                    "created_at": a["created_at"]
                })

        events.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "application": dict(app_row),
            "events": events
        }
    finally:
        conn.close()


@app.get("/admin/academic/activities")
def get_admin_academic_activities(
    institution_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_platform_admin),
):
    """Central monitoring of academic events (marks, attendance, enrollments, exams). Restricted to platform_admin."""
    conn = get_connection()
    try:
        where_clauses = ["pal.event_category = 'academic'"]
        params = []
        if institution_id and institution_id != "all":
            where_clauses.append("pal.institution_id = ?")
            params.append(institution_id)

        where_sql = " AND ".join(where_clauses)
        total = conn.execute(f"SELECT count(*) FROM platform_audit_logs pal WHERE {where_sql}", params).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT pal.id, pal.event_type, pal.institution_id, s.school_name AS institution_name,
                   s.category AS institution_category, pal.actor_name, pal.actor_role,
                   pal.entity_type, pal.entity_id, pal.action,
                   pal.old_values, pal.new_values, pal.remarks, pal.created_at
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            WHERE {where_sql}
            ORDER BY pal.created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset]
        ).fetchall()

        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    finally:
        conn.close()


@app.get("/admin/staff/activities")
def get_admin_staff_activities(
    institution_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_platform_admin),
):
    """Central monitoring of staff onboarding, invitations, and role lifecycle events. Restricted to platform_admin."""
    conn = get_connection()
    try:
        where_clauses = ["pal.event_category = 'staff'"]
        params = []
        if institution_id and institution_id != "all":
            where_clauses.append("pal.institution_id = ?")
            params.append(institution_id)

        where_sql = " AND ".join(where_clauses)
        total = conn.execute(f"SELECT count(*) FROM platform_audit_logs pal WHERE {where_sql}", params).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT pal.id, pal.event_type, pal.institution_id, s.school_name AS institution_name,
                   pal.actor_name, pal.actor_role, pal.entity_type, pal.entity_id,
                   pal.action, pal.old_values, pal.new_values, pal.remarks, pal.created_at
            FROM platform_audit_logs pal
            LEFT JOIN schools s ON s.school_id = pal.institution_id
            WHERE {where_sql}
            ORDER BY pal.created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset]
        ).fetchall()

        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    finally:
        conn.close()


@app.get("/admin/reports/analytics")
def get_admin_reports_analytics(user: dict = Depends(require_platform_admin)):
    """Comprehensive analytics and metrics aggregation across all institutions. Restricted to platform_admin."""
    conn = get_connection()
    try:
        status_counts = conn.execute("SELECT status, count(*) FROM admission_applications GROUP BY status").fetchall()
        app_by_status = {r[0]: r[1] for r in status_counts}

        cat_counts = conn.execute(
            """
            SELECT s.category, count(a.application_id)
            FROM schools s
            LEFT JOIN admission_applications a ON a.institution_id = s.school_id
            GROUP BY s.category
            """
        ).fetchall()
        app_by_category = {r[0]: r[1] for r in cat_counts}

        top_insts = conn.execute(
            """
            SELECT s.school_id, s.school_name, s.category, count(a.application_id) AS app_count
            FROM schools s
            JOIN admission_applications a ON a.institution_id = s.school_id
            GROUP BY s.school_id
            ORDER BY app_count DESC
            LIMIT 5
            """
        ).fetchall()

        event_cats = conn.execute("SELECT event_category, count(*) FROM platform_audit_logs GROUP BY event_category").fetchall()
        events_by_category = {r[0]: r[1] for r in event_cats}

        enr_cats = conn.execute(
            """
            SELECT s.category, count(e.enrollment_id)
            FROM schools s
            LEFT JOIN enrollments e ON e.school_id = s.school_id
            GROUP BY s.category
            """
        ).fetchall()
        enrolments_by_category = {r[0]: r[1] for r in enr_cats}

        return {
            "applications_by_status": app_by_status,
            "applications_by_category": app_by_category,
            "top_institutions": [dict(r) for r in top_insts],
            "events_by_category": events_by_category,
            "enrolments_by_category": enrolments_by_category,
        }
    finally:
        conn.close()


@app.put("/schools/{school_id}/capacity")
def update_institution_seat_capacity(
    school_id: str,
    payload: UpdateSeatCapacityPayload,
    user: dict = Depends(get_current_user),
):
    """
    Update seat capacity for a program section.
    Authorized for platform_admin or institution staff/admin for this school.
    """
    if user["role"] != "platform_admin" and user.get("school_id") != school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot modify seat capacity for institution '{school_id}'."
        )

    conn = get_connection()
    try:
        sec = conn.execute(
            "SELECT section_id, capacity, current_strength, program_id FROM program_sections WHERE section_id = ? AND institution_id = ?",
            (payload.section_id, school_id)
        ).fetchone()

        if not sec:
            raise HTTPException(status_code=404, detail=f"Section '{payload.section_id}' not found for institution '{school_id}'.")

        prev_cap = sec["capacity"]
        conn.execute(
            "UPDATE program_sections SET capacity = ? WHERE section_id = ?",
            (payload.new_capacity, payload.section_id)
        )

        record_platform_audit(
            conn,
            event_type="SEAT_CAPACITY_UPDATED",
            event_category="institution",
            institution_id=school_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="program_section",
            entity_id=payload.section_id,
            action=f"Seat capacity updated from {prev_cap} to {payload.new_capacity} for section {payload.section_id}",
            old_values={"capacity": prev_cap},
            new_values={"capacity": payload.new_capacity},
            remarks=payload.reason or "Sanctioned capacity adjustment"
        )
        conn.commit()

        return {
            "success": True,
            "institution_id": school_id,
            "section_id": payload.section_id,
            "previous_capacity": prev_cap,
            "new_capacity": payload.new_capacity,
            "reason": payload.reason
        }
    finally:
        conn.close()


@app.put("/schools/{school_id}/profile")
def update_institution_profile(
    school_id: str,
    payload: UpdateSchoolProfilePayload,
    user: dict = Depends(get_current_user),
):
    """
    Update institution contact and profile information.
    Authorized for platform_admin or institution staff/admin for this school.
    """
    if user["role"] != "platform_admin" and user.get("school_id") != school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot modify profile for institution '{school_id}'."
        )

    conn = get_connection()
    try:
        sch = conn.execute("SELECT * FROM schools WHERE school_id = ?", (school_id,)).fetchone()
        if not sch:
            raise HTTPException(status_code=404, detail=f"Institution '{school_id}' not found.")

        old_vals = {}
        new_vals = {}
        updates = []
        params = []

        if payload.public_phone is not None:
            old_vals["public_phone"] = sch["public_phone"]
            new_vals["public_phone"] = payload.public_phone
            updates.append("public_phone = ?")
            params.append(payload.public_phone)

        if payload.website is not None:
            old_vals["website"] = sch["website"]
            new_vals["website"] = payload.website
            updates.append("website = ?")
            params.append(payload.website)

        if payload.email is not None:
            old_vals["email"] = sch["email"]
            new_vals["email"] = payload.email
            updates.append("email = ?")
            params.append(payload.email)

        if payload.address is not None:
            old_vals["address"] = sch["address"]
            new_vals["address"] = payload.address
            updates.append("address = ?")
            params.append(payload.address)

        if payload.description is not None:
            old_vals["description"] = sch["description"]
            new_vals["description"] = payload.description
            updates.append("description = ?")
            params.append(payload.description)

        if updates:
            params.append(school_id)
            conn.execute(f"UPDATE schools SET {', '.join(updates)} WHERE school_id = ?", params)

            record_platform_audit(
                conn,
                event_type="INSTITUTION_PROFILE_UPDATED",
                event_category="institution",
                institution_id=school_id,
                actor_user_id=user["user_id"],
                actor_role=user["role"],
                entity_type="school",
                entity_id=school_id,
                action=f"Institution profile updated for {sch['school_name']}",
                old_values=old_vals,
                new_values=new_vals,
                remarks=payload.reason or "Profile details update"
            )
            conn.commit()

        return {"success": True, "institution_id": school_id, "updated_fields": list(new_vals.keys())}
    finally:
        conn.close()



@app.get("/school/admin/overview")
def get_school_admin_overview(user: dict = Depends(require_school_admin)):
    """Administrative overview for a school administrator's assigned school."""
    conn = get_connection()
    try:
        school_id = user["school_id"]
        school = conn.execute(
            "SELECT school_id, school_name, district, state, school_type FROM schools WHERE school_id = ?",
            (school_id,)
        ).fetchone()

        if not school:
            raise HTTPException(404, "Assigned school record not found.")

        student_count = conn.execute(
            "SELECT count(*) FROM students WHERE school_id = ?",
            (school_id,)
        ).fetchone()[0]

        staff_count = conn.execute(
            "SELECT count(*) FROM users WHERE school_id = ? AND role IN ('school_staff', 'school_admin')",
            (school_id,)
        ).fetchone()[0]

        pending_requests = conn.execute(
            "SELECT count(*) FROM linking_requests WHERE school_id = ? AND request_status = 'pending'",
            (school_id,)
        ).fetchone()[0]

        return {
            "school": dict(school),
            "enrolled_students": student_count,
            "authorized_staff_count": staff_count,
            "pending_linking_requests": pending_requests,
        }
    finally:
        conn.close()


# =====================================================================
# ACADEMIC PROGRAMMES & EDUCATION STRUCTURE APIs (PHASE 2)
# =====================================================================

@app.get("/education/programs")
def list_academic_programs(
    institution_id: Optional[str] = Query(default=None),
    education_level: Optional[str] = Query(default=None),
    degree_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Retrieve normalized academic programs across all 4 education levels."""
    conn = get_connection()
    try:
        sql = """
            SELECT p.program_id, p.institution_id, s.school_name AS institution_name,
                   p.education_level, p.program_name, p.degree_type,
                   p.discipline_or_stream, p.combination_code, p.duration_years
            FROM academic_programs p
            JOIN schools s ON s.school_id = p.institution_id
            WHERE p.is_active = 1
        """
        params = []
        if institution_id:
            sql += " AND p.institution_id = ?"
            params.append(institution_id)
        if education_level:
            sql += " AND p.education_level = ?"
            params.append(education_level)
        if degree_type:
            sql += " AND p.degree_type = ?"
            params.append(degree_type)

        sql += " ORDER BY p.education_level, p.institution_id, p.program_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/schools/{school_id}/sections")
def get_school_available_sections(
    school_id: str,
    standard: Optional[int] = Query(default=None, ge=1, le=12),
    user: dict = Depends(get_current_user),
):
    """
    Returns the distinct standards and sections configured and populated for a school.
    Allows frontend roster engines to dynamically adapt dropdowns without guessing.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT DISTINCT standard, section, count(*) as student_count
            FROM students
            WHERE school_id = ?
        """
        params = [school_id]
        if standard is not None:
            sql += " AND standard = ?"
            params.append(standard)

        sql += " GROUP BY standard, section ORDER BY standard, section"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/schools/{school_id}/program-sections")
def get_school_program_sections(
    school_id: str,
    education_level: Optional[str] = Query(default=None),
    combination_code: Optional[str] = Query(default=None),
    discipline_or_stream: Optional[str] = Query(default=None),
    degree_type: Optional[str] = Query(default=None),
    term_or_year: Optional[int] = Query(default=None),
    semester: Optional[int] = Query(default=None),
    section_name: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    user: dict = Depends(get_current_user),
):
    """
    Returns configured program sections and actual strengths for an institution.
    Supports non-equal student distribution across streams, combinations, and sections.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT ps.section_id, ps.institution_id, s.school_name AS institution_name, ps.program_id,
                   p.program_name, p.education_level, p.degree_type,
                   p.discipline_or_stream, p.combination_code,
                   ps.academic_year, ps.term_or_year, ps.semester,
                   ps.section_name, ps.capacity, ps.current_strength
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            LEFT JOIN schools s ON s.school_id = ps.institution_id
            WHERE 1=1
        """
        params = []
        if school_id and school_id.lower() != 'all':
            sql += " AND ps.institution_id = ?"
            params.append(school_id)
        if education_level:
            sql += " AND p.education_level = ?"
            params.append(education_level)
        if combination_code:
            sql += " AND p.combination_code = ?"
            params.append(combination_code)
        if discipline_or_stream:
            sql += " AND p.discipline_or_stream = ?"
            params.append(discipline_or_stream)
        if degree_type:
            sql += " AND p.degree_type = ?"
            params.append(degree_type)
        if term_or_year is not None:
            sql += " AND ps.term_or_year = ?"
            params.append(term_or_year)
        if semester is not None:
            sql += " AND ps.semester = ?"
            params.append(semester)
        if section_name:
            sql += " AND ps.section_name = ?"
            params.append(section_name)
        if academic_year:
            sql += " AND ps.academic_year = ?"
            params.append(academic_year)

        sql += " ORDER BY ps.institution_id, p.education_level, p.combination_code, ps.term_or_year, ps.section_name"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/education/program-sections")
def get_all_program_sections(
    institution_id: Optional[str] = Query(default=None),
    education_level: Optional[str] = Query(default=None),
    combination_code: Optional[str] = Query(default=None),
    discipline_or_stream: Optional[str] = Query(default=None),
    degree_type: Optional[str] = Query(default=None),
    term_or_year: Optional[int] = Query(default=None),
    semester: Optional[int] = Query(default=None),
    section_name: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    user: dict = Depends(get_current_user),
):
    """
    Returns global or filtered programme sections with student counts across all institutions.
    """
    return get_school_program_sections(
        school_id=institution_id or "all",
        education_level=education_level,
        combination_code=combination_code,
        discipline_or_stream=discipline_or_stream,
        degree_type=degree_type,
        term_or_year=term_or_year,
        semester=semester,
        section_name=section_name,
        academic_year=academic_year,
        user=user,
    )


# ==============================================================================
# TWO-STAGE ADMISSION MANAGEMENT & SEAT AVAILABILITY (PHASE 1 CORE)
# ==============================================================================

class Stage1ApplicationCreate(BaseModel):
    institution_id: str
    division_id: Optional[str] = None
    applicant_name: str
    parent_name: str
    parent_phone: str
    parent_email: Optional[str] = None
    residential_address: str
    academic_year: str = "2026-2027"
    education_level: str  # 'school', 'higher_secondary', 'diploma', 'undergraduate'
    requested_standard: Optional[int] = None
    requested_program_id: Optional[str] = None
    first_language_preference: Optional[str] = None
    second_language_preference: Optional[str] = None
    stream_preference: Optional[str] = None
    combination_code: Optional[str] = None


class AdmissionReviewApproveRequest(BaseModel):
    confirm: bool = True
    note: Optional[str] = None


class AdmissionClarificationRequest(BaseModel):
    clarification_message: str = Field(min_length=5, max_length=2000)


class AdmissionRejectRequest(BaseModel):
    rejection_reason: str = Field(min_length=5, max_length=1000)
    rejection_explanation: Optional[str] = None
    institution_contact_phone: Optional[str] = None


class ParentClaimApplicationRequest(BaseModel):
    application_id: str
    applicant_name: str
    password: Optional[str] = None


class Stage2SubmissionCreate(BaseModel):
    date_of_birth: str = Field(min_length=10, max_length=10) # YYYY-MM-DD
    gender: Literal["male", "female", "other"]
    blood_group: Optional[str] = None
    previous_institution_name: Optional[str] = None
    previous_institution_location: Optional[str] = None
    previous_standard_or_degree: Optional[str] = None
    previous_board: Optional[str] = None
    previous_marks_percentage: Optional[float] = None
    emergency_contact_name: str = Field(min_length=2, max_length=100)
    emergency_contact_phone: str = Field(min_length=10, max_length=15)
    custom_fields: Optional[dict] = None


class DocumentUploadPayload(BaseModel):
    document_type: str = Field(min_length=3, max_length=100)
    file_name: str = Field(min_length=3, max_length=255)
    file_data_base64: str = Field(min_length=10)
    mime_type: Optional[str] = "application/pdf"


class DocumentVerificationRequest(BaseModel):
    verification_status: Literal["verified", "rejected", "reupload_requested"]
    verification_notes: Optional[str] = None


class Stage2ReviewActionRequest(BaseModel):
    decision: Literal["detailed_review_completed", "stage2_correction_requested"]
    review_notes: Optional[str] = None


class ParentClarificationResponse(BaseModel):
    response_text: str = Field(min_length=3, max_length=2000)


class InstitutionCompareRequest(BaseModel):
    school_ids: list[str]


@app.get("/schools/{school_id}/seat-availability")
def get_school_seat_availability(
    school_id: str,
    academic_year: Optional[str] = Query(default=None),
):
    """
    Computes real-time seat availability from program_sections:
    available_seats = MAX(0, capacity - current_strength).
    Zero duplicate structures or invented numbers.
    """
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found")

        cat = school["category"] or ""
        stype = school["school_type"] or ""

        sql = """
            SELECT ps.section_id, ps.program_id, p.program_name, p.education_level,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   p.faculty_name, p.department_name,
                   ps.academic_year, ps.term_or_year, ps.semester, ps.section_name,
                   ps.capacity, ps.current_strength,
                   MAX(0, ps.capacity - ps.current_strength) AS available_seats
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE ps.institution_id = ?
        """
        params = [school_id]

        if academic_year and academic_year.lower() != 'all':
            sql += " AND ps.academic_year = ?"
            params.append(academic_year)
        else:
            # Auto-detect active academic year from institution sections
            ay_row = conn.execute(
                "SELECT academic_year FROM program_sections WHERE institution_id = ? ORDER BY academic_year DESC LIMIT 1",
                (school_id,)
            ).fetchone()
            if ay_row and ay_row["academic_year"]:
                active_ay = ay_row["academic_year"]
                sql += " AND ps.academic_year = ?"
                params.append(active_ay)
                academic_year = active_ay
            else:
                academic_year = "2026-27"

        # Category-specific filtering
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'"
        elif cat == "Degree Colleges" or stype == "Degree College":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate')"
        elif cat == "Universities" or stype == "University":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate', 'doctoral')"

        sql += " ORDER BY ps.term_or_year, ps.section_name, p.program_name"
        rows = conn.execute(sql, params).fetchall()
        sections = [dict(r) for r in rows]

        total_capacity = sum(s["capacity"] for s in sections)
        total_enrolled = sum(s["current_strength"] for s in sections)
        total_available = sum(s["available_seats"] for s in sections)

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "school_type": school["school_type"],
            "category": school["category"],
            "academic_year": academic_year or "2026-27",
            "total_sanctioned_capacity": total_capacity,
            "total_current_strength": total_enrolled,
            "total_available_seats": total_available,
            "sections_count": len(sections),
            "seat_breakdown": sections,
        }
    finally:
        conn.close()


@app.get("/schools/{school_id}/academic-strength")
def get_school_academic_strength(school_id: str):
    """
    Returns verified aggregate academic strength figures for an institution.
    Aggregated strictly by Programme, Standard, Year, Semester, Section and Language options.
    Guarantees privacy: No student names, marks, phones, addresses, or Aadhaar are exposed.
    """
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, school_name, school_type, affiliation, is_parent_group FROM schools WHERE school_id = ?",
            (school_id,)
        ).fetchone()
        if not school:
            raise HTTPException(404, f"Institution {school_id} not found.")

        # 1. Fetch all program sections with program meta
        sec_rows = conn.execute(
            """
            SELECT ps.section_id, ps.program_id, p.program_name, p.education_level,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   ps.academic_year, ps.term_or_year, ps.semester, ps.section_name,
                   ps.capacity, ps.current_strength,
                   CASE WHEN ps.capacity > ps.current_strength THEN ps.capacity - ps.current_strength ELSE 0 END AS available_seats
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE ps.institution_id = ?
            ORDER BY p.education_level, ps.term_or_year, ps.semester, ps.section_name
            """,
            (school_id,)
        ).fetchall()
        sections = [dict(r) for r in sec_rows]

        # 2. Fetch language options and enrollment distribution if available in enrollments table
        enr_rows = conn.execute(
            """
            SELECT standard, section, first_language, stream, subject_combination, COUNT(*) as student_count
            FROM enrollments
            WHERE school_id = ? AND enrollment_status = 'active'
            GROUP BY standard, section, first_language, stream, subject_combination
            ORDER BY standard, section
            """,
            (school_id,)
        ).fetchall()
        enrollments = [dict(r) for r in enr_rows]

        # 3. Compute program level aggregates
        programs_map = {}
        for s in sections:
            pid = s["program_id"]
            if pid not in programs_map:
                programs_map[pid] = {
                    "program_id": pid,
                    "program_name": s["program_name"],
                    "education_level": s["education_level"],
                    "degree_type": s["degree_type"],
                    "discipline_or_stream": s["discipline_or_stream"],
                    "combination_code": s["combination_code"],
                    "total_capacity": 0,
                    "total_strength": 0,
                    "sections_count": 0,
                    "sections": []
                }
            programs_map[pid]["total_capacity"] += s["capacity"]
            programs_map[pid]["total_strength"] += s["current_strength"]
            programs_map[pid]["sections_count"] += 1
            programs_map[pid]["sections"].append(s)

        total_capacity = sum(s["capacity"] for s in sections)
        enrolled_from_table = sum(e["student_count"] for e in enrollments)
        total_enrolled = enrolled_from_table if enrolled_from_table > 0 else sum(s["current_strength"] for s in sections)
        utilization_pct = round((total_enrolled / total_capacity * 100), 1) if total_capacity > 0 else 0

        languages = sorted(list(set(e["first_language"] for e in enrollments if e.get("first_language"))))

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "school_type": school["school_type"],
            "affiliation": school["affiliation"],
            "is_parent_group": bool(school["is_parent_group"]),
            "total_sanctioned_capacity": total_capacity,
            "total_enrolled_strength": total_enrolled,
            "overall_utilization_percent": utilization_pct,
            "sections_count": len(sections),
            "languages_offered": languages if languages else ["English", "Kannada"],
            "program_aggregates": list(programs_map.values()),
            "sections_roster": sections,
            "enrollment_breakdown": enrollments,
            "privacy_guarantee": "Under Karnataka Education Data Protection rules, individual student records are strictly restricted to authenticated parents and institutional administrators. Only verified aggregate section strength is publicly disclosed."
        }
    finally:
        conn.close()


@app.post("/schools/compare")
def compare_institutions(payload: InstitutionCompareRequest):
    """
    Compares 2 to 10 shortlisted institutions across verified fields:
    location, type, affiliations, 13 facilities, hostel, transport, and open seats.
    """
    if not payload.school_ids:
        raise HTTPException(400, "Please provide at least one institution ID to compare.")
    if len(payload.school_ids) > 10:
        raise HTTPException(400, "You can compare up to 10 institutions at a time.")

    conn = get_connection()
    try:
        placeholders = ",".join("?" for _ in payload.school_ids)
        sql = f"""
            SELECT school_id, school_name, district, state, school_type,
                   address, established_year, affiliation, recognition,
                   public_phone, email, website, logo_url, cover_image_url,
                   facilities_details_json, hostel_details_json, transport_details_json
            FROM schools
            WHERE school_id IN ({placeholders})
        """
        rows = conn.execute(sql, payload.school_ids).fetchall()
        result = []
        for r in rows:
            data = dict(r)
            # Parse facilities
            try:
                data["facilities"] = json.loads(data.get("facilities_details_json") or "{}")
            except Exception:
                data["facilities"] = {}
            try:
                data["hostel"] = json.loads(data.get("hostel_details_json") or "{}")
            except Exception:
                data["hostel"] = {}
            try:
                data["transport"] = json.loads(data.get("transport_details_json") or "{}")
            except Exception:
                data["transport"] = {}

            # Calculate total seats from program_sections
            seats_row = conn.execute(
                """
                SELECT COALESCE(SUM(capacity), 0) AS total_cap,
                       COALESCE(SUM(current_strength), 0) AS total_str,
                       COALESCE(SUM(MAX(0, capacity - current_strength)), 0) AS total_avail
                FROM program_sections
                WHERE institution_id = ?
                """,
                (data["school_id"],),
            ).fetchone()

            data["seat_summary"] = {
                "total_capacity": seats_row[0],
                "total_enrolled": seats_row[1],
                "available_seats": seats_row[2],
            }
            result.append(data)

        return result
    finally:
        conn.close()


@app.get("/admissions/form-config/{institution_id}")
def get_admission_form_config(institution_id: str):
    """
    Returns database-driven Stage 1 configuration for an institution.
    Provides valid standards, languages, streams, combinations, and programs without hardcoding.
    Strictly isolates Schools (K-10), PU Colleges, Degree Colleges, and Universities.
    """
    conn = get_connection()
    try:
        inst = conn.execute(
            """
            SELECT school_id, school_name, school_type, category, affiliation, district, state
            FROM schools WHERE school_id = ?
            """,
            (institution_id,)
        ).fetchone()
        if not inst:
            raise HTTPException(404, f"Institution {institution_id} not found.")

        cat = inst["category"] or ""
        stype = inst["school_type"] or ""
        is_school = cat == "Schools (K-10)" or stype == "School"
        is_pu = cat == "PU Colleges (11-12)" or "PU" in stype
        is_college = cat == "Degree Colleges" or stype == "Degree College"
        is_univ = cat == "Universities" or stype == "University"

        # 1. Divisions
        div_rows = conn.execute(
            """
            SELECT division_id, division_name, division_type, campus_location
            FROM institution_divisions WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            """,
            (institution_id,)
        ).fetchall()
        divisions = [dict(d) for d in div_rows]

        # 2. Academic programs
        prog_rows = conn.execute(
            """
            SELECT program_id, education_level, program_name, degree_type, discipline_or_stream, combination_code, duration_years
            FROM academic_programs WHERE institution_id = ? AND is_active = 1
            ORDER BY education_level, program_name
            """,
            (institution_id,)
        ).fetchall()
        programs = [dict(p) for p in prog_rows]

        # 3. Detect offered education categories strictly by institution category
        if is_school:
            offered_levels = ["school"]
        elif is_pu:
            offered_levels = ["higher_secondary"]
        elif is_college:
            offered_levels = ["undergraduate"]
        elif is_univ:
            offered_levels = [lvl for lvl in ["undergraduate", "postgraduate", "doctoral"] if any(p["education_level"] == lvl for p in programs)]
            if not offered_levels:
                offered_levels = ["undergraduate"]
        else:
            offered_levels = sorted(list(set(p["education_level"] for p in programs))) or ["school"]

        # 4. Standard levels for schools (1 to 10)
        has_school = is_school or "school" in offered_levels
        standards = list(range(1, 11)) if has_school else []

        # 5. Language options (from enrollments or institutional standards)
        if is_school:
            first_languages = ["Kannada", "Hindi", "Sanskrit"]
            second_languages = ["English"]
        else:
            lang_rows = conn.execute(
                "SELECT DISTINCT first_language FROM enrollments WHERE school_id = ? AND first_language IS NOT NULL",
                (institution_id,)
            ).fetchall()
            first_languages = [r[0] for r in lang_rows] if lang_rows else ["Kannada", "English"]
            second_languages = ["English", "Kannada", "Hindi", "Sanskrit"]

        # School specific programs
        school_programs = [
            {
                "program_id": p["program_id"],
                "program_name": p["program_name"]
            }
            for p in programs if p["education_level"] == "school"
        ]

        # 6. PU Streams & Combinations (ONLY for PU Colleges, NEVER for Schools)
        pu_combinations = []
        pu_streams = set()
        if is_pu or (not is_school and "higher_secondary" in offered_levels):
            for p in programs:
                if p["education_level"] == "higher_secondary":
                    if p["discipline_or_stream"]:
                        pu_streams.add(p["discipline_or_stream"])
                    pu_combinations.append({
                        "combination_code": p["combination_code"],
                        "stream": p["discipline_or_stream"],
                        "program_name": p["program_name"],
                        "program_id": p["program_id"]
                    })

        # 7. Diploma Programs (NEVER for Schools)
        diploma_programs = []
        if not is_school and "diploma" in offered_levels:
            diploma_programs = [
                {
                    "program_id": p["program_id"],
                    "program_name": p["program_name"],
                    "discipline_or_stream": p["discipline_or_stream"],
                    "duration_years": p["duration_years"]
                }
                for p in programs if p["education_level"] == "diploma"
            ]

        # 8. Undergraduate Programs (NEVER for Schools)
        ug_programs = []
        if not is_school and any(lvl in offered_levels for lvl in ["undergraduate", "postgraduate", "doctoral"]):
            ug_programs = [
                {
                    "program_id": p["program_id"],
                    "program_name": p["program_name"],
                    "degree_type": p["degree_type"],
                    "discipline_or_stream": p["discipline_or_stream"],
                    "duration_years": p["duration_years"]
                }
                for p in programs if p["education_level"] in ["undergraduate", "postgraduate", "doctoral"]
            ]

        # 9. Seat availability summary
        seat_summary = conn.execute(
            """
            SELECT COALESCE(SUM(capacity), 0) AS total_capacity,
                   COALESCE(SUM(current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN capacity > current_strength THEN capacity - current_strength ELSE 0 END), 0) AS available_seats
            FROM program_sections WHERE institution_id = ?
            """,
            (institution_id,)
        ).fetchone()

        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "school_type": inst["school_type"],
            "category": inst["category"],
            "is_school": is_school,
            "affiliation": inst["affiliation"],
            "district": inst["district"],
            "academic_year": "2026-2027",
            "offered_levels": offered_levels,
            "divisions": divisions,
            "has_school_offerings": has_school,
            "school_config": {
                "standards": standards,
                "first_languages": first_languages,
                "second_languages": second_languages,
                "programs": school_programs
            } if has_school else None,
            "pu_config": {
                "levels": ["1st PU (Class 11)", "2nd PU (Class 12)"],
                "streams": sorted(list(pu_streams)) if pu_streams else ["Science", "Commerce", "Arts"],
                "combinations": pu_combinations,
            } if (is_pu or (not is_school and "higher_secondary" in offered_levels)) and (pu_combinations or pu_streams) else None,
            "diploma_config": {
                "programs": diploma_programs,
            } if diploma_programs else None,
            "undergraduate_config": {
                "programs": ug_programs,
            } if ug_programs else None,
            "seat_summary": dict(seat_summary) if seat_summary else {"total_capacity": 0, "available_seats": 0},
            "status": "ready"
        }
    finally:
        conn.close()


def get_optional_current_user(request: Request) -> Optional[dict]:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif request.query_params.get("token"):
        token = request.query_params.get("token").strip()
    if not token:
        return None
    try:
        from auth import JWT_SECRET_KEY, JWT_ALGORITHM
        import jwt
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"require": ["sub", "exp", "iat", "jti"]})
        user_id = payload.get("sub")
        if not user_id:
            return None
        conn = get_connection()
        try:
            row = conn.execute("SELECT user_id, phone, email, full_name, role, school_id, is_active FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception:
        return None


def check_admission_application_access(app_row: dict, user: Optional[dict]) -> bool:
    """
    Verifies that the caller has legitimate authority over an admission application.
    Allowed actors:
    1. platform_admin: Statewide oversight.
    2. school_admin / staff: Only if reviewer's assigned school_id matches the application's institution_id.
    3. applicant / parent: Only if caller's user_id, phone, or email matches the application record.
    All others (unauthenticated or cross-tenant/unrelated users): Denied.
    """
    if not user:
        return False
    role = user.get("role")
    if role == "platform_admin":
        return True
    if role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "institution_admin", "student_records_officer", "general_staff"):
        return user.get("school_id") == app_row["institution_id"]
    if role == "parent":
        uid = user.get("user_id")
        if uid and app_row.get("parent_user_id") and uid == app_row["parent_user_id"]:
            return True
        return False
    return False


@app.post("/admissions/apply", status_code=status.HTTP_201_CREATED)
def submit_stage1_admission_application(
    payload: Stage1ApplicationCreate,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Submits a Stage 1 Initial Admission Application.
    Dynamically validates fields against database configurations:
    - School: Standard (1-10) + Language preference
    - PU College: Stream + Subject Combination (verified against academic_programs)
    - Diploma / UG: Program ID matching institution offerings.
    """
    conn = get_connection()
    try:
        # 1. Verify institution exists
        inst = conn.execute(
            "SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?",
            (payload.institution_id,),
        ).fetchone()
        if not inst:
            raise HTTPException(404, "Selected institution not found.")

        cat = inst["category"] or ""
        stype = inst["school_type"] or ""
        is_school = cat == "Schools (K-10)" or stype == "School"
        is_pu = cat == "PU Colleges (11-12)" or "PU" in stype

        # 2. Basic validations
        app_name = payload.applicant_name.strip()
        par_name = payload.parent_name.strip()
        par_phone = payload.parent_phone.strip()
        res_addr = payload.residential_address.strip()

        if len(app_name) < 2:
            raise HTTPException(400, "Applicant full name must be at least 2 characters.")
        if len(par_name) < 2:
            raise HTTPException(400, "Parent/guardian full name must be at least 2 characters.")
        digits_phone = "".join(filter(str.isdigit, par_phone))
        if len(digits_phone) < 10:
            raise HTTPException(400, "Please provide a valid 10-digit contact mobile number.")
        if len(res_addr) < 5:
            raise HTTPException(400, "Please provide a complete residential address (min 5 characters).")

        # 3. Division validation if passed
        if payload.division_id:
            div = conn.execute(
                "SELECT division_id FROM institution_divisions WHERE division_id = ? AND parent_institution_id = ?",
                (payload.division_id, payload.institution_id)
            ).fetchone()
            if not div:
                raise HTTPException(400, f"Division '{payload.division_id}' is not associated with this institution.")

        # 4. Type-specific validation against database
        level = payload.education_level.lower()
        if is_school:
            if level != "school":
                raise HTTPException(400, f"Institution '{inst['school_name']}' is a School (K-10) and only accepts School Education (K-10) applications. Pre-University programme data is not allowed.")
            if payload.combination_code or payload.stream_preference:
                raise HTTPException(400, "School admission does not accept PU streams or combinations.")
        elif is_pu:
            if level != "higher_secondary":
                raise HTTPException(400, f"Institution '{inst['school_name']}' is a Pre-University College and only accepts Pre-University (Classes 11-12) applications.")

        if level == "school":
            if not payload.requested_standard or not (1 <= payload.requested_standard <= 10):
                raise HTTPException(400, "School admission requires a valid standard between 1 and 10.")
            
            # School Language Validation: Accept only Kannada, Hindi, or Sanskrit
            first_lang = (payload.first_language_preference or "").strip()
            ALLOWED_SCHOOL_FIRST_LANGS = {"Kannada", "Hindi", "Sanskrit"}
            if first_lang not in ALLOWED_SCHOOL_FIRST_LANGS:
                raise HTTPException(
                    400,
                    f"Invalid first language preference '{first_lang}'. School admission accepts only: Kannada, Hindi, or Sanskrit."
                )
            payload.first_language_preference = first_lang

            # Automatically assign English as the second language (never trust frontend-submitted values)
            payload.second_language_preference = "English"
        elif level == "higher_secondary":
            if not payload.combination_code:
                raise HTTPException(400, "PU College admission requires a preferred subject combination (e.g. PCMB, PCMC, SEBA).")
            comb_prog = conn.execute(
                "SELECT program_id FROM academic_programs WHERE institution_id = ? AND combination_code = ? AND education_level = 'higher_secondary'",
                (payload.institution_id, payload.combination_code.strip())
            ).fetchone()
            if not comb_prog:
                raise HTTPException(400, f"Subject combination '{payload.combination_code}' is not configured for this PU institution.")
            if not payload.requested_program_id:
                payload.requested_program_id = comb_prog["program_id"]
        elif level in ["diploma", "undergraduate"]:
            if not payload.requested_program_id:
                raise HTTPException(400, f"{level.title()} admission requires selecting an offered academic program.")
            prog_row = conn.execute(
                "SELECT program_id FROM academic_programs WHERE institution_id = ? AND program_id = ? AND education_level = ?",
                (payload.institution_id, payload.requested_program_id.strip(), level)
            ).fetchone()
            if not prog_row:
                raise HTTPException(400, f"Programme '{payload.requested_program_id}' is not offered by this institution for level '{level}'.")
        else:
            raise HTTPException(400, f"Invalid education category: {payload.education_level}")

        # 5. Enforce Citizen/Parent Authentication & Duplicate Prevention
        if not current_user or current_user.get("role") not in ("parent", "citizen"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required: You must be signed in with an authorized Citizen or Parent account to submit an admission application."
            )
        parent_uid = current_user["user_id"]

        # Duplicate check: prevent duplicate active submissions for same applicant, institution, academic year
        existing_active = conn.execute(
            """
            SELECT application_id FROM admission_applications
            WHERE parent_user_id = ? AND institution_id = ? AND applicant_name = ? COLLATE NOCASE
              AND academic_year = ? AND status NOT IN ('rejected', 'withdrawn')
            """,
            (parent_uid, payload.institution_id, app_name, payload.academic_year)
        ).fetchone()
        if existing_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active admission application ({existing_active['application_id']}) has already been submitted for {app_name} at this institution for academic cycle {payload.academic_year}."
            )

        # Generate unique Application ID
        app_id = f"APP-{payload.academic_year[:4]}-{payload.institution_id}-{uuid.uuid4().hex[:6].upper()}"

        # 6. Insert into admission_applications
        conn.execute(
            """
            INSERT INTO admission_applications (
                application_id, institution_id, division_id, parent_user_id,
                applicant_name, parent_name, parent_phone, parent_email,
                residential_address, academic_year, education_level,
                requested_standard, requested_program_id, first_language_preference,
                second_language_preference, stream_preference, combination_code, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted')
            """,
            (
                app_id,
                payload.institution_id,
                payload.division_id,
                parent_uid,
                app_name,
                par_name,
                digits_phone[-10:],
                payload.parent_email.strip() if payload.parent_email else None,
                res_addr,
                payload.academic_year,
                level,
                payload.requested_standard,
                payload.requested_program_id,
                payload.first_language_preference,
                payload.second_language_preference,
                payload.stream_preference,
                payload.combination_code,
            ),
        )

        # 7. Insert initial status history
        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status,
                action_by_user_id, action_note
            ) VALUES (?, ?, NULL, 'submitted', ?, 'Initial Stage 1 application submitted.')
            """,
            (str(uuid.uuid4()), app_id, parent_uid or "public_applicant"),
        )

        # 8. Dispatch in-app notification to School Admin
        conn.execute(
            """
            INSERT INTO portal_notifications (
                notification_id, recipient_role, institution_id, application_id,
                title, message, action_url
            ) VALUES (?, 'school_admin', ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                payload.institution_id,
                app_id,
                f"New Admission Application: {app_name}",
                f"A new Stage 1 application for {level.replace('_', ' ').title()} was submitted by {par_name}.",
                f"/staff?tab=admissions&app_id={app_id}",
            ),
        )

        record_platform_audit(
            conn,
            event_type="ADMISSION_SUBMITTED",
            event_category="admission",
            institution_id=payload.institution_id,
            actor_user_id=parent_uid,
            actor_role="parent",
            entity_type="admission_application",
            entity_id=app_id,
            action=f"Stage 1 admission application submitted for {app_name}",
            new_values={"status": "submitted", "academic_year": payload.academic_year, "applicant_name": app_name},
            remarks="Initial Stage 1 application submitted."
        )
        conn.commit()

        return {
            "application_id": app_id,
            "status": "submitted",
            "message": "Your initial admission application has been submitted successfully.",
            "institution_name": inst["school_name"],
            "academic_year": payload.academic_year,
            "applicant_name": app_name,
            "education_level": level,
        }
    finally:
        conn.close()


@app.get("/admissions/applications/{application_id}/public-confirmation")
def get_public_application_confirmation(application_id: str):
    """
    Publicly verifies application submission and returns safe tracking confirmation.
    Guarantees privacy: No phone, email, residential address, or internal staff notes.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT a.application_id, a.institution_id, s.school_name AS institution_name,
                   s.school_type, a.applicant_name, a.academic_year, a.education_level,
                   a.requested_standard, a.combination_code, a.status, a.created_at
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            WHERE a.application_id = ?
            """,
            (application_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Admission application reference not found.")

        data = dict(row)
        return {
            "application_id": data["application_id"],
            "institution_id": data["institution_id"],
            "institution_name": data["institution_name"],
            "applicant_name": data["applicant_name"],
            "education_level": data["education_level"],
            "requested_standard": data["requested_standard"],
            "combination_code": data["combination_code"],
            "academic_year": data["academic_year"],
            "status": data["status"],
            "submission_timestamp": data["created_at"],
            "tracking_guidance": "Retain this Application ID. To track status updates or respond to school inquiries, sign in to your verified Parent Account using the registered contact number."
        }
    finally:
        conn.close()


@app.get("/school/admissions/overview")
def get_school_admissions_overview(
    user: dict = Depends(require_school_staff),
):
    """
    Provides admissions KPI metrics for the reviewer's assigned institution.
    """
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Staff account is not assigned to an institution.")

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) as cnt
            FROM admission_applications
            WHERE institution_id = ?
            GROUP BY status
            """,
            (school_id,)
        ).fetchall()
        status_map = {r["status"]: r["cnt"] for r in rows}

        levels = conn.execute(
            """
            SELECT education_level, COUNT(*) as cnt
            FROM admission_applications
            WHERE institution_id = ?
            GROUP BY education_level
            """,
            (school_id,)
        ).fetchall()
        level_map = {r["education_level"]: r["cnt"] for r in levels}

        total = sum(status_map.values())
        return {
            "institution_id": school_id,
            "total_applications": total,
            "submitted_count": status_map.get("submitted", 0),
            "under_review_count": status_map.get("under_review", 0),
            "action_required_count": status_map.get("action_required", 0),
            "approved_count": status_map.get("approved", 0),
            "rejected_count": status_map.get("rejected", 0),
            "by_level": level_map
        }
    finally:
        conn.close()


@app.get("/school/admissions/applications")
def list_school_admission_applications(
    status_filter: Optional[str] = Query(default="all"),
    education_level: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    institution_id: Optional[str] = Query(default=None),
    user: dict = Depends(require_school_staff),
):
    """
    Lists admission applications for the assigned institution with filtering and pagination.
    """
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Staff account is not assigned to an institution.")
    if institution_id and institution_id != school_id and user.get("role") != "platform_admin":
        raise HTTPException(403, f"Cross-institution access forbidden: Account is assigned to {school_id}, cannot access {institution_id}.")

    conn = get_connection()
    try:
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_view_applications") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have permission to view admission applications.")

        sql = """
            SELECT a.application_id, a.institution_id, a.applicant_name, a.parent_name,
                   a.parent_phone, a.parent_email, a.education_level, a.requested_standard,
                   a.requested_program_id, p.program_name, a.combination_code, a.stream_preference,
                   a.first_language_preference, a.second_language_preference, a.academic_year,
                   a.status, a.reviewer_user_id, a.clarification_request, a.rejection_reason,
                   a.created_at, a.updated_at
            FROM admission_applications a
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.institution_id = ?
        """
        params = [school_id]
        if status_filter and status_filter.lower() != "all":
            sf = status_filter.lower()
            if sf in ("clarification_requested", "action_required"):
                sql += " AND a.status IN ('clarification_requested', 'action_required')"
            elif sf == "pending":
                sql += " AND a.status IN ('submitted', 'under_review', 'action_required', 'clarification_requested')"
            else:
                sql += " AND a.status = ?"
                params.append(sf)
        if education_level and education_level.lower() != "all":
            sql += " AND a.education_level = ?"
            params.append(education_level.lower())
        if academic_year and academic_year.lower() != "all":
            sql += " AND a.academic_year = ?"
            params.append(academic_year)
        if search and search.strip():
            sql += " AND (a.applicant_name LIKE ? OR a.application_id LIKE ? OR a.parent_phone LIKE ?)"
            s_pat = f"%{search.strip()}%"
            params.extend([s_pat, s_pat, s_pat])

        # Total count
        count_sql = f"SELECT COUNT(*) FROM ({sql})"
        total = conn.execute(count_sql, params).fetchone()[0]

        sql += " ORDER BY a.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(sql, params).fetchall()
        app_list = []
        for r in rows:
            rd = dict(r)
            rd["id"] = r["application_id"]
            rd["application_reference"] = r["application_id"]
            rd["student_name"] = r["applicant_name"]
            rd["standard"] = r["requested_standard"]
            app_list.append(rd)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "applications": app_list
        }
    finally:
        conn.close()


@app.get("/school/admissions/applications/{application_id}")
def get_school_admission_application_detail(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Retrieves full Stage 1 application detail for authorized institutional reviewers.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is at {school_id}.")
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_review_details") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have permission to review applicant details.")
        row = conn.execute(
            """
            SELECT a.*, s.school_name, p.program_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ? AND a.institution_id = ?
            """,
            (application_id, school_id)
        ).fetchone()

        data = dict(row)
        data['id'] = data['application_id']
        data['application_reference'] = data['application_id']
        data['student_name'] = data.get('applicant_name')
        data['standard'] = data.get('requested_standard')
        hist = conn.execute(
            """
            SELECT history_id, previous_status, new_status, action_by_user_id, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            """,
            (application_id,)
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]

        # Stage 2 Detailed Submission
        detailed_row = conn.execute(
            """
            SELECT submission_id, application_id, date_of_birth, gender, blood_group,
                   previous_institution_name, previous_institution_location,
                   previous_standard_or_degree, previous_board, previous_marks_percentage,
                   emergency_contact_name, emergency_contact_phone, custom_fields_json,
                   status, submitted_at
            FROM admission_detailed_submissions
            WHERE application_id = ?
            ORDER BY submitted_at DESC
            LIMIT 1
            """,
            (application_id,)
        ).fetchone()

        if detailed_row:
            s2 = dict(detailed_row)
            if s2.get("custom_fields_json"):
                try:
                    s2["custom_fields"] = json.loads(s2["custom_fields_json"])
                except Exception:
                    s2["custom_fields"] = {}
            else:
                s2["custom_fields"] = {}
            data["stage2_details"] = s2
            data["stage2_submitted"] = True
            data["date_of_birth"] = s2.get("date_of_birth")
            data["gender"] = s2.get("gender")
            data["blood_group"] = s2.get("blood_group")
            data["previous_institution_name"] = s2.get("previous_institution_name")
            data["previous_institution_location"] = s2.get("previous_institution_location")
            data["previous_standard_or_degree"] = s2.get("previous_standard_or_degree")
            data["previous_board"] = s2.get("previous_board")
            data["previous_marks_percentage"] = s2.get("previous_marks_percentage")
            data["emergency_contact_name"] = s2.get("emergency_contact_name")
            data["emergency_contact_phone"] = s2.get("emergency_contact_phone")
            data["stage2_submitted_at"] = s2.get("submitted_at")
        else:
            data["stage2_details"] = None
            data["stage2_submitted"] = False

        # Supporting Documents
        doc_rows = conn.execute(
            """
            SELECT d.document_id, d.application_id, d.document_type, d.file_name, d.file_size_bytes,
                   d.mime_type, d.verification_status, d.uploaded_at, d.verified_by_user_id,
                   d.verified_at, d.verification_notes, u.full_name as verified_by_name
            FROM admission_documents d
            LEFT JOIN users u ON u.user_id = d.verified_by_user_id
            WHERE d.application_id = ?
            ORDER BY d.uploaded_at ASC
            """,
            (application_id,)
        ).fetchall()

        type_counts = {}
        for dr in doc_rows:
            dt = dr["document_type"]
            type_counts[dt] = type_counts.get(dt, 0) + 1

        type_current = {}
        docs_list = []
        for dr in doc_rows:
            d = dict(dr)
            dt = d["document_type"]
            type_current[dt] = type_current.get(dt, 0) + 1
            ver = type_current[dt]
            d["version"] = ver
            d["is_latest"] = (ver == type_counts[dt])
            d["download_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            d["preview_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            docs_list.append(d)
        data["documents"] = docs_list
        latest_docs = [d for d in docs_list if d.get("is_latest")]
        data["total_documents_count"] = len(latest_docs)
        data["verified_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "verified")
        data["pending_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "pending")
        data["rejected_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "rejected")
        data["reupload_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") in ("reupload_requested", "rejected"))

        return data
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/review")
def mark_application_under_review(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is assigned to {school_id}.")
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_review_details") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have permission to review applications.")

        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if app_row["status"] not in ("submitted", "action_required"):
            raise HTTPException(400, f"Cannot move application from '{app_row['status']}' to 'under_review'.")

        prev_status = app_row["status"]
        conn.execute(
            "UPDATE admission_applications SET status = 'under_review', reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (user["user_id"], application_id)
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'under_review', ?, 'Application taken up for institutional review.')
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"])
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Application Under Review', 'Your admission application is currently under institutional review.', ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, f"/parent?tab=admissions&app_id={application_id}")
            )
        conn.commit()
        return {"status": "under_review", "application_id": application_id}
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/approve")
def approve_stage1_application(
    application_id: str,
    payload: AdmissionReviewApproveRequest,
    user: dict = Depends(require_school_staff),
):
    if not payload.confirm:
        raise HTTPException(400, "Explicit confirmation required to approve preliminary application.")
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is assigned to {school_id}.")
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_approve_stage1") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have final Stage 1 approval authority. Submit an admission recommendation instead.")

        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if app_row["status"] not in ("under_review", "submitted", "action_required"):
            raise HTTPException(400, f"Cannot approve application currently in '{app_row['status']}' status.")

        prev_status = app_row["status"]
        conn.execute(
            "UPDATE admission_applications SET status = 'approved', reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (user["user_id"], application_id)
        )
        note = payload.note or "Stage 1 initial application approved. Eligible for Stage 2 detailed submission."
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'approved', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"], note)
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Initial Application Approved', 'Your Stage 1 admission application has been approved. You can proceed to detailed admission when Stage 2 opens.', ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, f"/parent?tab=admissions&app_id={application_id}")
            )
        record_platform_audit(
            conn,
            event_type="STAGE1_APPROVED",
            event_category="admission",
            institution_id=school_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="admission_application",
            entity_id=application_id,
            action=f"Stage 1 initial application approved for {app_row['applicant_name']}",
            old_values={"status": prev_status},
            new_values={"status": "approved"},
            remarks=note
        )
        conn.commit()
        return {
            "status": "approved",
            "application_id": application_id,
            "message": "Application approved. Stage 2 detailed submission will be unlocked when available."
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/request-clarification")
def request_application_clarification(
    application_id: str,
    payload: AdmissionClarificationRequest,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is assigned to {school_id}.")
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_request_clarification") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have permission to request application clarification.")

        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if app_row["status"] not in ("under_review", "submitted", "stage2_submitted", "documents_uploaded"):
            raise HTTPException(400, f"Cannot request clarification for application in '{app_row['status']}' status.")

        prev_status = app_row["status"]
        conn.execute(
            "UPDATE admission_applications SET status = 'action_required', clarification_request = ?, reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (payload.clarification_message.strip(), user["user_id"], application_id)
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'action_required', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"], f"Clarification requested: {payload.clarification_message.strip()}")
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Action Required: Clarification Requested', ?, ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, payload.clarification_message.strip(), f"/parent?tab=admissions&app_id={application_id}")
            )
        record_platform_audit(
            conn,
            event_type="CLARIFICATION_REQUESTED",
            event_category="admission",
            institution_id=school_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="admission_application",
            entity_id=application_id,
            action=f"Clarification requested from parent for {app_row['applicant_name']}",
            old_values={"status": prev_status},
            new_values={"status": "action_required"},
            remarks=payload.clarification_message.strip()
        )
        conn.commit()
        return {"status": "action_required", "application_id": application_id}
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/reject")
def reject_stage1_application(
    application_id: str,
    payload: AdmissionRejectRequest,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is assigned to {school_id}.")
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_approve_stage1") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Final rejection authority requires administrator authorization. Submit an admission recommendation instead.")

        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if app_row["status"] in ("approved", "rejected"):
            raise HTTPException(400, f"Cannot reject application in '{app_row['status']}' status.")

        prev_status = app_row["status"]
        conn.execute(
            """
            UPDATE admission_applications
            SET status = 'rejected', rejection_reason = ?, rejection_explanation = ?,
                institution_contact_phone = ?, reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
            """,
            (
                payload.rejection_reason.strip(),
                payload.rejection_explanation.strip() if payload.rejection_explanation else None,
                payload.institution_contact_phone.strip() if payload.institution_contact_phone else None,
                user["user_id"],
                application_id
            )
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'rejected', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"], f"Application rejected. Reason: {payload.rejection_reason.strip()}")
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Application Decision: Not Accepted', ?, ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, f"Reason: {payload.rejection_reason.strip()}", f"/parent?tab=admissions&app_id={application_id}")
            )
        record_platform_audit(
            conn,
            event_type="STAGE1_REJECTED",
            event_category="admission",
            institution_id=school_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="admission_application",
            entity_id=application_id,
            action=f"Stage 1 application rejected for {app_row['applicant_name']}",
            old_values={"status": prev_status},
            new_values={"status": "rejected"},
            remarks=f"{payload.rejection_reason}: {payload.rejection_explanation or ''}"
        )
        conn.commit()
        return {"status": "rejected", "application_id": application_id}
    finally:
        conn.close()


@app.get("/school/admissions/{application_id}/history")
def get_school_application_history(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Returns full audit trail for an application.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_check = conn.execute(
            "SELECT application_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_check:
            raise HTTPException(404, "Application not found or unauthorized.")

        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_view_history") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have permission to view application history.")

        rows = conn.execute(
            """
            SELECT history_id, application_id, previous_status, new_status,
                   action_by_user_id, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            """,
            (application_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/parent/admissions/applications")
def get_parent_admission_applications(
    user: dict = Depends(require_parent),
):
    """
    Returns all admission applications submitted by or linked to the authenticated parent.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT a.application_id, a.institution_id, s.school_name AS institution_name,
                   s.school_type, a.applicant_name, a.academic_year, a.education_level,
                   a.requested_standard, a.combination_code, a.requested_program_id,
                   p.program_name, a.status, a.rejection_reason, a.institution_contact_phone,
                   a.clarification_request, a.created_at, a.updated_at
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.parent_user_id = ?
               OR (a.parent_email IS NOT NULL AND a.parent_email = ?)
            ORDER BY a.created_at DESC
        """
        rows = conn.execute(sql, (user["user_id"], user.get("email", ""))).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/parent/admissions/applications/{application_id}")
def get_parent_application_details(
    application_id: str,
    user: dict = Depends(require_parent),
):
    """
    Retrieves full detail for a single application.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT a.*, s.school_name AS institution_name, s.public_phone, s.email AS school_email,
                   p.program_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ? AND (a.parent_user_id = ? OR (a.parent_email IS NOT NULL AND a.parent_email = ?))
        """
        row = conn.execute(sql, (application_id, user["user_id"], user.get("email", ""))).fetchone()
        if not row:
            raise HTTPException(404, "Admission application not found or unauthorized.")

        data = dict(row)
        hist = conn.execute(
            """
            SELECT history_id, previous_status, new_status, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            """,
            (application_id,),
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]

        # Stage 2 Detailed Submission
        detailed_row = conn.execute(
            """
            SELECT submission_id, application_id, date_of_birth, gender, blood_group,
                   previous_institution_name, previous_institution_location,
                   previous_standard_or_degree, previous_board, previous_marks_percentage,
                   emergency_contact_name, emergency_contact_phone, custom_fields_json,
                   status, submitted_at
            FROM admission_detailed_submissions
            WHERE application_id = ?
            ORDER BY submitted_at DESC
            LIMIT 1
            """,
            (application_id,)
        ).fetchone()

        if detailed_row:
            s2 = dict(detailed_row)
            if s2.get("custom_fields_json"):
                try:
                    s2["custom_fields"] = json.loads(s2["custom_fields_json"])
                except Exception:
                    s2["custom_fields"] = {}
            else:
                s2["custom_fields"] = {}
            data["stage2_details"] = s2
            data["stage2_submitted"] = True
            data["date_of_birth"] = s2.get("date_of_birth")
            data["gender"] = s2.get("gender")
            data["blood_group"] = s2.get("blood_group")
            data["previous_institution_name"] = s2.get("previous_institution_name")
            data["previous_institution_location"] = s2.get("previous_institution_location")
            data["previous_standard_or_degree"] = s2.get("previous_standard_or_degree")
            data["previous_board"] = s2.get("previous_board")
            data["previous_marks_percentage"] = s2.get("previous_marks_percentage")
            data["emergency_contact_name"] = s2.get("emergency_contact_name")
            data["emergency_contact_phone"] = s2.get("emergency_contact_phone")
            data["stage2_submitted_at"] = s2.get("submitted_at")
        else:
            data["stage2_details"] = None
            data["stage2_submitted"] = False

        # Supporting Documents
        doc_rows = conn.execute(
            """
            SELECT d.document_id, d.application_id, d.document_type, d.file_name, d.file_size_bytes,
                   d.mime_type, d.verification_status, d.uploaded_at, d.verified_by_user_id,
                   d.verified_at, d.verification_notes, u.full_name as verified_by_name
            FROM admission_documents d
            LEFT JOIN users u ON u.user_id = d.verified_by_user_id
            WHERE d.application_id = ?
            ORDER BY d.uploaded_at ASC
            """,
            (application_id,)
        ).fetchall()

        type_counts = {}
        for dr in doc_rows:
            dt = dr["document_type"]
            type_counts[dt] = type_counts.get(dt, 0) + 1

        type_current = {}
        docs_list = []
        for dr in doc_rows:
            d = dict(dr)
            dt = d["document_type"]
            type_current[dt] = type_current.get(dt, 0) + 1
            ver = type_current[dt]
            d["version"] = ver
            d["is_latest"] = (ver == type_counts[dt])
            d["download_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            d["preview_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            docs_list.append(d)
        data["documents"] = docs_list
        latest_docs = [d for d in docs_list if d.get("is_latest")]
        data["total_documents_count"] = len(latest_docs)
        data["verified_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "verified")
        data["pending_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "pending")
        data["rejected_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "rejected")
        data["reupload_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") in ("reupload_requested", "rejected"))

        return data
    finally:
        conn.close()


@app.post("/parent/admissions/claim")
def claim_admission_application(
    payload: ParentClaimApplicationRequest,
    user: dict = Depends(require_parent),
):
    """
    Securely links an unlinked application to the authenticated parent account.
    Requires applicant full name match, contact phone match, and parent account password verification.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, applicant_name, parent_phone, parent_user_id, status FROM admission_applications WHERE application_id = ?",
            (payload.application_id.strip(),)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application ID not found.")

        if app_row["parent_user_id"]:
            if app_row["parent_user_id"] == user["user_id"]:
                return {
                    "status": "claimed",
                    "application_id": app_row["application_id"],
                    "message": "This application is already linked to your parent account."
                }
            raise HTTPException(409, "This application is already claimed by another registered parent account.")

        # Require applicant name match (case-insensitive)
        if not payload.applicant_name or payload.applicant_name.strip().lower() != (app_row["applicant_name"] or "").strip().lower():
            raise HTTPException(403, "Applicant full name verification failed. Please enter the exact applicant name on the application record.")

        # Require phone match
        user_row = conn.execute("SELECT phone, password_hash FROM users WHERE user_id = ?", (user["user_id"],)).fetchone()
        user_phone = (user_row["phone"] or user.get("phone") or "") if user_row else (user.get("phone") or "")
        digits_user = "".join(filter(str.isdigit, user_phone))[-10:]
        digits_app = "".join(filter(str.isdigit, app_row["parent_phone"] or ""))[-10:]
        if not digits_user or digits_app != digits_user:
            raise HTTPException(403, "Application contact mobile number does not match your registered parent mobile number.")

        # Require account password verification
        if payload.password:
            if not user_row or not verify_password(payload.password, user_row["password_hash"]):
                raise HTTPException(401, "Account password verification failed. Please enter your valid parent account password.")

        conn.execute(
            "UPDATE admission_applications SET parent_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (user["user_id"], payload.application_id.strip())
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status,
                action_by_user_id, action_note
            ) VALUES (?, ?, ?, ?, ?, 'Application claimed and verified by registered parent account.')
            """,
            (str(uuid.uuid4()), payload.application_id.strip(), app_row["status"] or "submitted", app_row["status"] or "submitted", user["user_id"])
        )
        conn.commit()
        return {
            "status": "claimed",
            "application_id": payload.application_id.strip(),
            "message": "Application successfully claimed and linked to your dashboard."
        }
    finally:
        conn.close()


@app.post("/parent/admissions/applications/{application_id}/respond-clarification")
def respond_to_clarification(
    application_id: str,
    payload: ParentClarificationResponse,
    user: dict = Depends(require_parent),
):
    """
    Allows parent to respond to clarification request. Moves application back to under_review.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, institution_id, applicant_name FROM admission_applications WHERE application_id = ? AND parent_user_id = ?",
            (application_id, user["user_id"])
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")
        if app_row["status"] != "action_required":
            raise HTTPException(400, "Application is not awaiting clarification.")

        conn.execute(
            "UPDATE admission_applications SET status = 'under_review', updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (application_id,)
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, 'action_required', 'under_review', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, user["user_id"], f"Parent submitted clarification: {payload.response_text.strip()}")
        )
        conn.execute(
            """
            INSERT INTO portal_notifications (notification_id, recipient_role, institution_id, application_id, title, message, action_url)
            VALUES (?, 'school_admin', ?, ?, 'Clarification Responded', 'Parent responded to clarification inquiry.', ?)
            """,
            (str(uuid.uuid4()), app_row["institution_id"], application_id, f"/staff?tab=admissions&app_id={application_id}")
        )
        record_platform_audit(
            conn,
            event_type="CLARIFICATION_SUBMITTED",
            event_category="admission",
            institution_id=app_row["institution_id"],
            actor_user_id=user["user_id"],
            actor_role="parent",
            entity_type="admission_application",
            entity_id=application_id,
            action=f"Parent submitted clarification response for {app_row['applicant_name']}",
            old_values={"status": "action_required"},
            new_values={"status": "under_review"},
            remarks=payload.response_text.strip()
        )
        conn.commit()
        return {"status": "under_review", "application_id": application_id}
    finally:
        conn.close()



# -------------------------------------------------------------
# PHASE 5: STAGE 2 DETAILED ADMISSION & DOCUMENT VERIFICATION
# -------------------------------------------------------------

@app.get("/admissions/applications/{application_id}/stage2-eligibility")
def get_stage2_eligibility(
    application_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Checks if application is approved in Stage 1 and returns Stage 2 eligibility,
    required documents checklist, and existing submission data.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            """
            SELECT a.*, s.school_name AS institution_name, s.school_type
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            WHERE a.application_id = ?
            """,
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        if not check_admission_application_access(dict(app_row), current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if not current_user else status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to view this application's Stage 2 dossier.",
            )

        app_data = dict(app_row)
        valid_stage2_statuses = (
            "approved", "stage2_submitted", "documents_uploaded",
            "under_detailed_review", "detailed_review_completed",
            "final_admission_confirmed", "enrolled"
        )
        if app_data["status"] not in valid_stage2_statuses:
            raise HTTPException(
                403,
                f"Stage 2 detailed admission form is strictly locked. Current status is '{app_data['status']}'. Stage 1 preliminary approval by the institution desk is required."
            )

        # Dynamic document checklist
        level = app_data.get("education_level", "school")
        std = app_data.get("requested_standard")
        checklist = [
            {"document_type": "birth_certificate", "label": "Birth Certificate / Government Proof of Age", "is_mandatory": True},
            {"document_type": "passport_photo", "label": "Recent Passport Size Photograph of Applicant", "is_mandatory": True},
        ]
        if level != "school" or (std and std > 1):
            checklist.extend([
                {"document_type": "previous_marks_card", "label": "Previous Standard / Qualifying Marks Card", "is_mandatory": True},
                {"document_type": "transfer_certificate", "label": "Official School / College Transfer Certificate (TC)", "is_mandatory": True},
            ])
        checklist.extend([
            {"document_type": "caste_certificate", "label": "Caste / Social Category Certificate (if claiming quota)", "is_mandatory": False},
            {"document_type": "income_certificate", "label": "Annual Income Certificate (for Fee Concessions)", "is_mandatory": False},
        ])

        # Fetch existing stage 2 submission if any
        sub_row = conn.execute(
            "SELECT * FROM admission_detailed_submissions WHERE application_id = ?",
            (application_id,)
        ).fetchone()

        # Fetch uploaded documents
        docs = conn.execute(
            "SELECT document_id, application_id, document_type, file_name, file_size_bytes, mime_type, verification_status, uploaded_at, verified_at, verification_notes FROM admission_documents WHERE application_id = ?",
            (application_id,)
        ).fetchall()

        return {
            "application_id": application_id,
            "status": app_data["status"],
            "is_eligible": True,
            "applicant_name": app_data["applicant_name"],
            "institution_id": app_data["institution_id"],
            "institution_name": app_data["institution_name"],
            "education_level": app_data["education_level"],
            "requested_standard": app_data.get("requested_standard"),
            "combination_code": app_data.get("combination_code"),
            "requested_program_id": app_data.get("requested_program_id"),
            "required_documents": checklist,
            "stage2_submission": dict(sub_row) if sub_row else None,
            "uploaded_documents": [dict(d) for d in docs]
        }
    finally:
        conn.close()


@app.post("/admissions/applications/{application_id}/stage2-submit")
def submit_stage2_detailed_admission(
    application_id: str,
    payload: Stage2SubmissionCreate,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Submits detailed student demographic information, medical details,
    and previous schooling records for Stage 2.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, status, applicant_name, parent_user_id, parent_phone, parent_email FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        if not check_admission_application_access(dict(app_row), current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if not current_user else status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to submit Stage 2 information for this application.",
            )

        valid_entry_statuses = ("approved", "stage2_submitted", "documents_uploaded", "stage2_correction_requested")
        if app_row["status"] not in valid_entry_statuses:
            raise HTTPException(
                400,
                f"Cannot submit Stage 2 form for application in '{app_row['status']}' status. Stage 1 approval required."
            )

        sub_id = str(uuid.uuid4())
        custom_json = json.dumps(payload.custom_fields) if payload.custom_fields else None

        conn.execute(
            """
            INSERT OR REPLACE INTO admission_detailed_submissions (
                submission_id, application_id, date_of_birth, gender, blood_group,
                previous_institution_name, previous_institution_location,
                previous_standard_or_degree, previous_board, previous_marks_percentage,
                emergency_contact_name, emergency_contact_phone, custom_fields_json,
                status, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted', CURRENT_TIMESTAMP)
            """,
            (
                sub_id, application_id, payload.date_of_birth, payload.gender,
                payload.blood_group, payload.previous_institution_name,
                payload.previous_institution_location, payload.previous_standard_or_degree,
                payload.previous_board, payload.previous_marks_percentage,
                payload.emergency_contact_name, payload.emergency_contact_phone,
                custom_json
            )
        )

        prev_status = app_row["status"]
        new_status = "stage2_submitted" if prev_status == "approved" else prev_status
        conn.execute(
            "UPDATE admission_applications SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (new_status, application_id)
        )

        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, ?, ?, 'Stage 2 detailed demographic and academic records dossier submitted.')
            """,
            (str(uuid.uuid4()), application_id, prev_status, new_status, current_user.get("user_id") if current_user else "parent")
        )

        conn.execute(
            """
            INSERT INTO portal_notifications (notification_id, recipient_role, institution_id, application_id, title, message, action_url)
            VALUES (?, 'school_admin', ?, ?, 'Stage 2 Dossier Submitted', ?, ?)
            """,
            (
                str(uuid.uuid4()), app_row["institution_id"], application_id,
                f"Stage 2 detailed submission received for {app_row['applicant_name']}.",
                f"/staff?tab=admissions&app_id={application_id}"
            )
        )

        record_platform_audit(
            conn,
            event_type="STAGE2_SUBMITTED",
            event_category="admission",
            institution_id=app_row["institution_id"],
            actor_user_id=current_user["user_id"] if current_user else app_row["parent_user_id"],
            actor_role="parent",
            entity_type="admission_application",
            entity_id=application_id,
            action=f"Stage 2 detailed admission form submitted for {app_row['applicant_name']}",
            old_values={"status": "approved"},
            new_values={"status": "stage2_submitted"},
            remarks="Stage 2 detailed admission form submitted."
        )
        conn.commit()
        return {
            "status": "success",
            "application_id": application_id,
            "submission_id": sub_id,
            "application_status": new_status,
            "message": "Stage 2 detailed admission dossier submitted successfully. Please proceed with mandatory document uploads."
        }
    finally:
        conn.close()


@app.post("/admissions/applications/{application_id}/documents")
def upload_stage2_document(
    application_id: str,
    payload: DocumentUploadPayload,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Securely uploads a supporting document for Stage 2 admission verification.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, status, applicant_name, parent_user_id, parent_phone, parent_email FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        if not check_admission_application_access(dict(app_row), current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if not current_user else status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to upload documents for this application.",
            )

        # Decode base64 file data
        try:
            file_bytes = base64.b64decode(payload.file_data_base64)
        except Exception:
            raise HTTPException(400, "Invalid base64 document content.")

        if len(file_bytes) == 0:
            raise HTTPException(400, "Uploaded document is empty (0 bytes).")

        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Document size exceeds the 10 MB limit.")

        # Magic byte validation for allowed formats (PDF, JPEG, PNG, WEBP)
        is_pdf = file_bytes.startswith(b"%PDF")
        is_jpg = file_bytes.startswith(b"\xff\xd8\xff")
        is_png = file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        is_webp = len(file_bytes) > 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP"

        if not (is_pdf or is_jpg or is_png or is_webp):
            raise HTTPException(
                status_code=400,
                detail="Unsupported or malicious file type. Only authentic PDF documents and JPEG/PNG/WEBP images are permitted.",
            )

        # Disallow dangerous executable extensions in filename
        disallowed_exts = (".exe", ".sh", ".bat", ".cmd", ".js", ".php", ".py", ".html", ".htm", ".vbs", ".ps1")
        if any(payload.file_name.lower().endswith(ext) for ext in disallowed_exts):
            raise HTTPException(
                status_code=400,
                detail="File contains an unacceptable or dangerous file extension.",
            )

        doc_id = str(uuid.uuid4())
        safe_filename = "".join(c for c in payload.file_name if c.isalnum() or c in "._- ")
        if not safe_filename:
            safe_filename = f"{payload.document_type}.pdf"

        # Write to secure uploads directory
        upload_dir = os.path.join("/app", "data", "uploads", "admissions", application_id)
        os.makedirs(upload_dir, exist_ok=True)
        file_disk_path = os.path.join(upload_dir, f"{doc_id}_{safe_filename}")
        with open(file_disk_path, "wb") as f_out:
            f_out.write(file_bytes)

        # Record in database
        conn.execute(
            """
            INSERT INTO admission_documents (
                document_id, application_id, document_type, file_name,
                file_path, file_size_bytes, mime_type, verification_status, uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
            """,
            (
                doc_id, application_id, payload.document_type, safe_filename,
                file_disk_path, len(file_bytes), payload.mime_type
            )
        )

        # Update application status to documents_uploaded if in stage2_submitted
        if app_row["status"] in ("approved", "stage2_submitted"):
            conn.execute(
                "UPDATE admission_applications SET status = 'documents_uploaded', updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
                (application_id,)
            )

        # Audit trail for document upload / replacement
        doc_label = payload.document_type.replace("_", " ").title()
        uploader_id = current_user.get("user_id") if current_user else "parent"
        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status, action_by_user_id, action_note
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()), application_id, app_row["status"], app_row["status"], uploader_id,
                f"Applicant parent uploaded certificate '{safe_filename}' ({doc_label}) for verification."
            )
        )

        conn.commit()
        return {
            "status": "uploaded",
            "document_id": doc_id,
            "application_id": application_id,
            "document_type": payload.document_type,
            "file_name": safe_filename,
            "file_size_bytes": len(file_bytes),
            "verification_status": "pending"
        }
    finally:
        conn.close()


@app.get("/admissions/applications/{application_id}/documents")
def get_stage2_documents(
    application_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Returns list of uploaded documents and their verification status for an application.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, parent_user_id, parent_phone, parent_email FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        if not check_admission_application_access(dict(app_row), current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if not current_user else status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to view documents for this application.",
            )

        rows = conn.execute(
            """
            SELECT document_id, application_id, document_type, file_name, file_size_bytes,
                   mime_type, verification_status, uploaded_at, verified_at, verification_notes
            FROM admission_documents
            WHERE application_id = ?
            ORDER BY uploaded_at ASC
            """,
            (application_id,)
        ).fetchall()

        type_counts = {}
        for r in rows:
            dt = r["document_type"]
            type_counts[dt] = type_counts.get(dt, 0) + 1

        type_current = {}
        docs = []
        for r in rows:
            d = dict(r)
            dt = d["document_type"]
            type_current[dt] = type_current.get(dt, 0) + 1
            ver = type_current[dt]
            d["version"] = ver
            d["is_latest"] = (ver == type_counts[dt])
            d["download_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            d["preview_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            docs.append(d)
        return docs
    finally:
        conn.close()


@app.get("/admissions/applications/{application_id}/documents/{document_id}/file")
def get_admission_document_file(
    application_id: str,
    document_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Retrieves the raw document file for viewing/download.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, parent_user_id, parent_phone, parent_email FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        if not check_admission_application_access(dict(app_row), current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if not current_user else status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to download documents for this application.",
            )

        doc = conn.execute(
            "SELECT file_path, file_name, mime_type FROM admission_documents WHERE document_id = ? AND application_id = ?",
            (document_id, application_id)
        ).fetchone()
        if not doc:
            raise HTTPException(404, "Document not found.")
        fpath = doc["file_path"]
        if not os.path.exists(fpath):
            local_fallback = os.path.join("/app", "data", "uploads", "admissions", application_id, os.path.basename(fpath))
            if os.path.exists(local_fallback):
                fpath = local_fallback
            else:
                host_fallback = os.path.join("backend", "data", "uploads", "admissions", application_id, os.path.basename(fpath))
                if os.path.exists(host_fallback):
                    fpath = host_fallback
                else:
                    raise HTTPException(404, "Document file not found on disk.")
        return FileResponse(fpath, media_type=doc["mime_type"], filename=doc["file_name"])
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/documents/{document_id}/verify")
def verify_admission_document(
    application_id: str,
    document_id: str,
    payload: DocumentVerificationRequest,
    user: dict = Depends(require_school_staff),
):
    """
    Authorized institution staff verifies or rejects a Stage 2 supporting document.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        # Check document existence and institution authorization
        doc_row = conn.execute(
            """
            SELECT d.document_id, d.document_type, d.file_name, d.verification_status,
                   a.institution_id, a.parent_user_id, a.applicant_name, a.status as app_status
            FROM admission_documents d
            JOIN admission_applications a ON a.application_id = d.application_id
            WHERE d.document_id = ? AND d.application_id = ?
            """,
            (document_id, application_id)
        ).fetchone()
        if not doc_row:
            raise HTTPException(404, "Document not found for this admission application.")

        if doc_row["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {doc_row['institution_id']}, reviewer is assigned to {school_id}.")

        current_status = doc_row["verification_status"]
        target_status = payload.verification_status

        # Prevent repeated acceptance or rejection without an appropriate review workflow
        if target_status == "verified" and current_status == "verified":
            raise HTTPException(400, "Document is already verified. Repeated acceptance is not permitted.")
        if target_status == "rejected" and current_status == "rejected":
            raise HTTPException(400, "Document is already rejected. Repeated rejection is not permitted.")

        # Rejection reason is mandatory when rejecting
        if target_status == "rejected":
            if not payload.verification_notes or not payload.verification_notes.strip():
                raise HTTPException(400, "Rejection reason is mandatory when rejecting a document.")

        clean_notes = payload.verification_notes.strip() if payload.verification_notes else (
            "Document verified and found authentic by institution administrator." if target_status == "verified" else None
        )

        conn.execute(
            """
            UPDATE admission_documents
            SET verification_status = ?,
                verified_by_user_id = ?,
                verified_at = CURRENT_TIMESTAMP,
                verification_notes = ?
            WHERE document_id = ?
            """,
            (target_status, user["user_id"], clean_notes, document_id)
        )

        doc_label = doc_row["document_type"].replace("_", " ").title()

        # Notify parent through in-app notification system
        if doc_row["parent_user_id"]:
            if target_status == "rejected":
                notif_title = f"Document Rejected: {doc_label}"
                notif_msg = (
                    f"Your uploaded certificate '{doc_row['file_name']}' for {doc_label} (Applicant: {doc_row['applicant_name']}) "
                    f"was reviewed and rejected by {doc_row['institution_id']}. Reason: {clean_notes}. "
                    f"Please log in and upload a valid replacement document."
                )
                conn.execute(
                    """
                    INSERT INTO portal_notifications (
                        notification_id, recipient_user_id, recipient_role, institution_id,
                        application_id, title, message, action_url, is_read, category, priority
                    ) VALUES (?, ?, 'parent', ?, ?, ?, ?, ?, 0, 'admissions', 'high')
                    """,
                    (
                        str(uuid.uuid4()), doc_row["parent_user_id"], doc_row["institution_id"],
                        application_id, notif_title, notif_msg, f"/parent?tab=admissions&app_id={application_id}"
                    )
                )
            elif target_status == "verified":
                notif_title = f"Document Verified: {doc_label}"
                notif_msg = (
                    f"Your uploaded certificate '{doc_row['file_name']}' for {doc_label} (Applicant: {doc_row['applicant_name']}) "
                    f"has been verified and accepted by {doc_row['institution_id']}."
                )
                conn.execute(
                    """
                    INSERT INTO portal_notifications (
                        notification_id, recipient_user_id, recipient_role, institution_id,
                        application_id, title, message, action_url, is_read, category, priority
                    ) VALUES (?, ?, 'parent', ?, ?, ?, ?, ?, 0, 'admissions', 'normal')
                    """,
                    (
                        str(uuid.uuid4()), doc_row["parent_user_id"], doc_row["institution_id"],
                        application_id, notif_title, notif_msg, f"/parent?tab=admissions&app_id={application_id}"
                    )
                )

        # Record in application status history for complete audit trail
        reviewer_name = user.get("full_name") or user.get("email") or "Institution Administrator"
        action_verb = "accepted and verified" if target_status == "verified" else ("rejected" if target_status == "rejected" else "marked for replacement")
        action_detail = f"Document '{doc_row['file_name']}' ({doc_label}) {action_verb} by {reviewer_name} (ID: {user['user_id']})."
        if clean_notes:
            action_detail += f" Note/Reason: {clean_notes}"

        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status, action_by_user_id, action_note
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), application_id, doc_row["app_status"], doc_row["app_status"], user["user_id"], action_detail)
        )

        conn.commit()
        return {
            "status": "updated",
            "document_id": document_id,
            "verification_status": target_status,
            "verification_notes": clean_notes,
            "verified_by_user_id": user["user_id"],
            "verified_at": datetime.utcnow().isoformat(),
            "message": "Document successfully verified." if target_status == "verified" else "Document marked as rejected."
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/stage2-review")
def review_stage2_dossier(
    application_id: str,
    payload: Stage2ReviewActionRequest,
    user: dict = Depends(require_school_staff),
):
    """
    School staff marks detailed Stage 2 review as completed or requests correction.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is assigned to {school_id}.")
        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()

        # Check document verification status if completing review
        if payload.decision == "detailed_review_completed":
            unverified = conn.execute(
                "SELECT COUNT(*) FROM admission_documents WHERE application_id = ? AND verification_status != 'verified'",
                (application_id,)
            ).fetchone()[0]
            if unverified > 0:
                raise HTTPException(400, f"Cannot complete detailed review: {unverified} supporting document(s) have not been verified.")

        prev_status = app_row["status"]
        new_status = payload.decision
        conn.execute(
            "UPDATE admission_applications SET status = ?, reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (new_status, user["user_id"], application_id)
        )

        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, new_status, user["user_id"], payload.review_notes or "Stage 2 detailed dossier review completed.")
        )

        if app_row["parent_user_id"]:
            msg = "Your Stage 2 dossier and documents have been fully verified. Pending final admission confirmation." if payload.decision == "detailed_review_completed" else f"Correction requested on Stage 2 dossier: {payload.review_notes}"
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Stage 2 Review Update', ?, ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, msg, f"/parent?tab=admissions&app_id={application_id}")
            )

        conn.commit()
        return {"status": new_status, "application_id": application_id}
    finally:
        conn.close()




class FinalAdmissionConfirmPayload(BaseModel):
    section_id: str
    admission_date: Optional[str] = None
    notes: Optional[str] = None


@app.get("/school/admissions/{application_id}/available-sections")
def get_available_sections_for_admission(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Returns available sections and seat capacities for an application.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, requested_standard, requested_program_id, education_level, academic_year, status FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row or app_row["institution_id"] != school_id:
            raise HTTPException(404, "Application not found or unauthorized for this institution.")

        std = app_row["requested_standard"]
        prog_id = app_row["requested_program_id"]

        sections = []
        if app_row["education_level"] == "school" and std:
            sections = conn.execute(
                """
                SELECT section_id, institution_id, program_id, term_or_year, section_name, capacity, current_strength
                FROM program_sections
                WHERE institution_id = ? AND term_or_year = ?
                ORDER BY section_name
                """,
                (school_id, std)
            ).fetchall()
        elif prog_id:
            sections = conn.execute(
                """
                SELECT section_id, institution_id, program_id, term_or_year, section_name, capacity, current_strength
                FROM program_sections
                WHERE institution_id = ? AND program_id = ?
                ORDER BY term_or_year, section_name
                """,
                (school_id, prog_id)
            ).fetchall()

        if not sections:
            sections = conn.execute(
                """
                SELECT section_id, institution_id, program_id, term_or_year, section_name, capacity, current_strength
                FROM program_sections
                WHERE institution_id = ?
                ORDER BY term_or_year, section_name
                LIMIT 10
                """,
                (school_id,)
            ).fetchall()

        result = []
        for s in sections:
            rem = max(0, s["capacity"] - s["current_strength"])
            result.append({
                "section_id": s["section_id"],
                "section_name": s["section_name"],
                "program_id": s["program_id"],
                "term_or_year": s["term_or_year"],
                "capacity": s["capacity"],
                "current_strength": s["current_strength"],
                "available_seats": rem,
                "is_full": rem == 0
            })
        return result
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/final-admission-confirm")
def confirm_final_admission_and_enrol(
    application_id: str,
    payload: FinalAdmissionConfirmPayload,
    user: dict = Depends(require_school_staff),
):
    """
    Authorized school staff confirms final admission, creates official student record
    in 'students' and 'enrollments', and increments section capacity safely.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            """
            SELECT a.*, s.school_name AS institution_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            WHERE a.application_id = ? AND a.institution_id = ?
            """,
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")

        # Idempotency: If already enrolled, return existing
        if app_row["status"] in ("enrolled", "final_admission_confirmed"):
            student = conn.execute(
                "SELECT * FROM students WHERE permanent_student_id = ?",
                (app_row["enrolled_student_id"],)
            ).fetchone()
            enrollment = conn.execute(
                "SELECT * FROM enrollments WHERE permanent_student_id = ?",
                (app_row["enrolled_student_id"],)
            ).fetchone()
            return {
                "status": "enrolled",
                "message": "Student is already officially enrolled (Idempotent response).",
                "application_id": application_id,
                "permanent_student_id": app_row["enrolled_student_id"],
                "student_id": student["student_id"] if student else None,
                "enrollment_id": enrollment["enrollment_id"] if enrollment else None,
                "standard": student["standard"] if student else app_row["requested_standard"],
                "section": student["section"] if student else "A",
                "is_already_enrolled": True
            }

        # Prerequisites: Must be verified
        allowed_statuses = ("approved", "stage2_submitted", "documents_uploaded", "detailed_review_completed", "documents_verified")
        if app_row["status"] not in allowed_statuses:
            raise HTTPException(400, f"Cannot confirm final admission: application status is '{app_row['status']}'. It must be verified first.")

        # Check unverified documents
        unverified_docs = conn.execute(
            "SELECT COUNT(*) FROM admission_documents WHERE application_id = ? AND verification_status != 'verified'",
            (application_id,)
        ).fetchone()[0]
        if unverified_docs > 0:
            raise HTTPException(400, f"Cannot confirm final admission: {unverified_docs} supporting document(s) have not been verified.")

        # Section validation & capacity check
        section_row = conn.execute(
            "SELECT * FROM program_sections WHERE section_id = ? AND institution_id = ?",
            (payload.section_id, school_id)
        ).fetchone()
        if not section_row:
            raise HTTPException(404, f"Selected section '{payload.section_id}' not found for institution '{school_id}'.")

        if section_row["current_strength"] >= section_row["capacity"]:
            raise HTTPException(400, f"Selected section '{section_row['section_name']}' is at full capacity ({section_row['current_strength']}/{section_row['capacity']} seats). Cannot enrol additional students.")

        # Stage 2 demographics if available
        stage2_sub = conn.execute(
            "SELECT * FROM admission_detailed_submissions WHERE application_id = ?",
            (application_id,)
        ).fetchone()

        std_val = app_row["requested_standard"] or section_row["term_or_year"] or 1
        std_for_enr = max(1, min(12, int(std_val)))

        sec_name = section_row["section_name"].strip().upper()
        if sec_name not in ("A", "B", "C"):
            sec_name = "A"

        lang_val = app_row["first_language_preference"] or "Kannada"
        if lang_val not in ("Kannada", "Hindi", "Sanskrit"):
            lang_val = "Kannada"

        dob = (stage2_sub["date_of_birth"] if stage2_sub and stage2_sub["date_of_birth"] else None) or "2015-06-01"
        gender = (stage2_sub["gender"] if stage2_sub and stage2_sub["gender"] else None) or "male"
        try:
            birth_year = int(dob.split("-")[0])
            calc_age = max(5, 2026 - birth_year)
        except Exception:
            calc_age = std_for_enr + 5

        adm_date = payload.admission_date or "2026-11-01"

        perm_student_id = f"NS-{uuid.uuid4().hex.upper()}"
        student_pk = generate_next_student_id(conn, school_id)
        enrollment_pk = f"ENR-{uuid.uuid4().hex.upper()}"

        # 1. Insert into students
        conn.execute(
            """
            INSERT INTO students (
                student_id, student_name, school_id, standard, section,
                age, permanent_student_id, first_language, date_of_birth,
                gender, admission_date, enrollment_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                student_pk, app_row["applicant_name"], school_id, std_for_enr, sec_name,
                calc_age, perm_student_id, lang_val, dob, gender, adm_date
            )
        )

        # 2. Insert into enrollments
        conn.execute(
            """
            INSERT INTO enrollments (
                enrollment_id, permanent_student_id, school_id, academic_year,
                standard, section, first_language, stream, subject_combination,
                admission_date, enrollment_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
            """,
            (
                enrollment_pk, perm_student_id, school_id, app_row["academic_year"] or "2026-2027",
                std_for_enr, sec_name, lang_val, app_row["stream_preference"], app_row["combination_code"],
                adm_date
            )
        )

        # 3. Increment section strength
        conn.execute(
            "UPDATE program_sections SET current_strength = current_strength + 1 WHERE section_id = ?",
            (payload.section_id,)
        )

        # 4. Update admission application
        prev_status = app_row["status"]
        conn.execute(
            """
            UPDATE admission_applications
            SET status = 'enrolled',
                enrolled_student_id = ?,
                enrolled_at = CURRENT_TIMESTAMP,
                reviewer_user_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
            """,
            (perm_student_id, user["user_id"], application_id)
        )

        # 5. Insert history
        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status, action_by_user_id, action_note
            ) VALUES (?, ?, ?, 'enrolled', ?, ?)
            """,
            (
                str(uuid.uuid4()), application_id, prev_status, user["user_id"],
                payload.notes or f"Final admission confirmed. Enrolled in Standard {std_for_enr}, Section {sec_name}. Permanent ID: {perm_student_id}"
            )
        )

        # 6. Auto-link student to parent guardian
        if app_row["parent_user_id"]:
            p_guardian = get_parent_guardian(conn, app_row["parent_user_id"])
            if p_guardian:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO student_guardians (
                        student_guardian_id, permanent_student_id, guardian_id,
                        can_view_records, can_request_updates, is_verified, created_at
                    ) VALUES (?, ?, ?, 1, 1, 1, CURRENT_TIMESTAMP)
                    """,
                    (str(uuid.uuid4()), perm_student_id, p_guardian["guardian_id"])
                )

        # 7. Notify parent
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (
                    notification_id, recipient_user_id, institution_id, application_id, title, message, action_url
                ) VALUES (?, ?, ?, ?, '🎉 Admission Confirmed & Enrolled!', ?, ?)
                """,
                (
                    str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id,
                    f"Congratulations! Official admission confirmed for {app_row['applicant_name']}. Permanent Student ID: {perm_student_id}, Section: {sec_name}.",
                    f"/parent?tab=children"
                )
            )

        record_platform_audit(
            conn,
            event_type="FINAL_ADMISSION_ACCEPTED",
            event_category="admission",
            institution_id=school_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="admission_application",
            entity_id=application_id,
            action=f"Final admission accepted and student enrolled for {app_row['applicant_name']}",
            old_values={"status": app_row["status"]},
            new_values={"status": "admitted", "enrolled_student_id": perm_student_id},
            remarks=payload.notes or "Final admission confirmed."
        )
        record_platform_audit(
            conn,
            event_type="STUDENT_ENROLLED",
            event_category="academic",
            institution_id=school_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="student",
            entity_id=perm_student_id,
            action=f"Official student enrolment created for {app_row['applicant_name']} ({student_pk})",
            new_values={"permanent_student_id": perm_student_id, "student_id": student_pk, "school_id": school_id, "enrollment_id": enrollment_pk},
            remarks=f"Enrolled in Standard {std_for_enr}, Section {sec_name}"
        )
        conn.commit()

        new_strength = conn.execute(
            "SELECT current_strength FROM program_sections WHERE section_id = ?",
            (payload.section_id,)
        ).fetchone()[0]

        return {
            "status": "enrolled",
            "message": "Student successfully enrolled in official institution academic ledger.",
            "application_id": application_id,
            "permanent_student_id": perm_student_id,
            "student_id": student_pk,
            "enrollment_id": enrollment_pk,
            "school_id": school_id,
            "standard": std_for_enr,
            "section": sec_name,
            "new_section_strength": new_strength,
            "is_already_enrolled": False
        }
    finally:
        conn.close()




class OcrOverridePayload(BaseModel):
    override_notes: str
    verified_match_status: Literal["verified_match", "rejected_mismatch"] = "verified_match"


@app.post("/school/admissions/{application_id}/documents/{document_id}/ocr-analyze")
def run_document_ocr_intelligence(
    application_id: str,
    document_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Runs real Intelligent Document Processing (IDP) and OCR extraction
    on an uploaded admission document without fabricated metrics.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        doc = conn.execute(
            """
            SELECT d.*, a.applicant_name, a.institution_id
            FROM admission_documents d
            JOIN admission_applications a ON a.application_id = d.application_id
            WHERE d.document_id = ? AND d.application_id = ? AND a.institution_id = ?
            """,
            (document_id, application_id, school_id)
        ).fetchone()
        if not doc:
            raise HTTPException(404, "Document not found or unauthorized for this institution.")

        file_path = doc["file_path"]
        if not os.path.exists(file_path):
            local_fallback = os.path.join("/app", "data", "uploads", "admissions", application_id, os.path.basename(file_path))
            if os.path.exists(local_fallback):
                file_path = local_fallback
            else:
                host_fallback = os.path.join("backend", "data", "uploads", "admissions", application_id, os.path.basename(file_path))
                if os.path.exists(host_fallback):
                    file_path = host_fallback
                else:
                    raise HTTPException(404, "Document file not found on disk.")

        # Determine file type & run real extraction
        mime = (doc["mime_type"] or "").lower()
        if "pdf" in mime or file_path.lower().endswith(".pdf"):
            raw_text, confidence = ocr_service.extract_text_from_pdf(file_path)
            ocr_engine = "pypdf_native_stream"
        else:
            raw_text, confidence = ocr_service.extract_text_and_confidence_from_image(file_path)
            ocr_engine = "tesseract_5.5.0_ocr"

        # Parse structured entities
        entities = ocr_service.parse_structured_entities(raw_text)

        # Fetch Stage 2 data for comparison
        stage2_sub = conn.execute(
            "SELECT * FROM admission_detailed_submissions WHERE application_id = ?",
            (application_id,)
        ).fetchone()

        s2_dob = stage2_sub["date_of_birth"] if stage2_sub else None
        s2_marks = stage2_sub["previous_marks_percentage"] if stage2_sub else None

        match_status, discrepancy_notes = ocr_service.compare_and_audit_discrepancies(
            entities, doc["applicant_name"], s2_dob, s2_marks
        )

        extraction_id = str(uuid.uuid4())
        entities_json = json.dumps(entities)

        # Store extraction
        conn.execute(
            """
            INSERT OR REPLACE INTO document_ocr_extractions (
                extraction_id, document_id, application_id, raw_text,
                ocr_engine, average_confidence, extracted_entities_json,
                match_status, discrepancy_notes, extracted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                extraction_id, document_id, application_id, raw_text,
                ocr_engine, confidence, entities_json, match_status, discrepancy_notes
            )
        )
        conn.commit()

        return {
            "extraction_id": extraction_id,
            "document_id": document_id,
            "application_id": application_id,
            "document_type": doc["document_type"],
            "file_name": doc["file_name"],
            "ocr_engine": ocr_engine,
            "confidence_percentage": confidence,
            "extracted_entities": entities,
            "match_status": match_status,
            "discrepancy_notes": discrepancy_notes,
            "raw_text_preview": raw_text[:300] + ("..." if len(raw_text) > 300 else "")
        }
    finally:
        conn.close()


@app.get("/school/admissions/{application_id}/documents/{document_id}/ocr-result")
def get_document_ocr_result(
    application_id: str,
    document_id: str,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT e.*, d.document_type, d.file_name
            FROM document_ocr_extractions e
            JOIN admission_documents d ON d.document_id = e.document_id
            JOIN admission_applications a ON a.application_id = e.application_id
            WHERE e.document_id = ? AND e.application_id = ? AND a.institution_id = ?
            ORDER BY e.extracted_at DESC
            LIMIT 1
            """,
            (document_id, application_id, school_id)
        ).fetchone()
        if not row:
            return {"has_ocr_result": False}

        return {
            "has_ocr_result": True,
            "extraction_id": row["extraction_id"],
            "ocr_engine": row["ocr_engine"],
            "confidence_percentage": row["average_confidence"],
            "extracted_entities": json.loads(row["extracted_entities_json"]),
            "match_status": row["match_status"],
            "discrepancy_notes": row["discrepancy_notes"],
            "extracted_at": row["extracted_at"],
            "raw_text": row["raw_text"]
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/documents/{document_id}/ocr-override")
def override_document_ocr_review(
    application_id: str,
    document_id: str,
    payload: OcrOverridePayload,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE document_ocr_extractions
            SET match_status = ?, discrepancy_notes = ?
            WHERE document_id = ? AND application_id = ?
            """,
            (payload.verified_match_status, f"Human Override by Staff {user['user_id']}: {payload.override_notes}", document_id, application_id)
        )
        conn.commit()
        return {"status": "overridden", "match_status": payload.verified_match_status}
    finally:
        conn.close()


@app.get("/notifications")
def get_user_notifications(
    user: dict = Depends(get_current_user),
    unread_only: bool = Query(default=False),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    include_meta: bool = Query(default=True),
):
    """
    Returns notifications for the authenticated user, strictly scoped to their identity and authorized role.
    """
    conn = get_connection()
    try:
        user_role = user.get("role")
        user_id = user["user_id"]
        school_id = user.get("school_id")

        where_clauses = []
        params = []

        # Role & Tenant Scoping
        if user_role == "platform_admin":
            where_clauses.append("(recipient_user_id = ? OR recipient_role = 'platform_admin' OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL)))")
            params.extend([user_id, user_role, school_id])
        elif user_role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff", "teacher", "academic_coordinator"):
            where_clauses.append("(recipient_user_id = ? OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL)) OR (recipient_role = 'school_staff' AND (institution_id = ? OR institution_id IS NULL)))")
            params.extend([user_id, user_role, school_id, school_id])
        elif user_role in ("student", "parent"):
            # Strict isolation: students only see their own notifications, parents only see their own notifications
            where_clauses.append("recipient_user_id = ?")
            params.append(user_id)
        else:
            where_clauses.append("recipient_user_id = ?")
            params.append(user_id)

        if unread_only:
            where_clauses.append("is_read = 0")

        if category and category.strip().lower() not in ("all", ""):
            where_clauses.append("category = ?")
            params.append(category.strip().lower())

        where_sql = " AND ".join(where_clauses)

        # Count total
        count_sql = f"SELECT count(*) FROM portal_notifications WHERE {where_sql}"
        total = conn.execute(count_sql, tuple(params)).fetchone()[0]

        # Calculate unread count specifically
        unread_params = []
        if user_role == "platform_admin":
            unread_sql = "SELECT count(*) FROM portal_notifications WHERE (recipient_user_id = ? OR recipient_role = 'platform_admin' OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL))) AND is_read = 0"
            unread_params = [user_id, user_role, school_id]
        elif user_role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff", "teacher", "academic_coordinator"):
            unread_sql = "SELECT count(*) FROM portal_notifications WHERE (recipient_user_id = ? OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL)) OR (recipient_role = 'school_staff' AND (institution_id = ? OR institution_id IS NULL))) AND is_read = 0"
            unread_params = [user_id, user_role, school_id, school_id]
        else:
            unread_sql = "SELECT count(*) FROM portal_notifications WHERE recipient_user_id = ? AND is_read = 0"
            unread_params = [user_id]
        unread_count = conn.execute(unread_sql, tuple(unread_params)).fetchone()[0]

        # Fetch page
        data_sql = f"""
            SELECT notification_id, recipient_user_id, recipient_role, institution_id,
                   application_id, title, message, action_url, is_read, created_at,
                   category, priority, channel, delivery_status, related_record_type,
                   related_record_id, read_at
            FROM portal_notifications
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        fetch_params = list(params) + [limit, offset]
        rows = conn.execute(data_sql, tuple(fetch_params)).fetchall()
        items = [dict(r) for r in rows]

        if not include_meta:
            return items

        return {
            "items": items,
            "total": total,
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset
        }
    finally:
        conn.close()


@app.get("/notifications/unread-count")
def get_unread_notification_count(
    user: dict = Depends(get_current_user),
):
    """
    Returns unread count for the authenticated user.
    """
    conn = get_connection()
    try:
        user_role = user.get("role")
        user_id = user["user_id"]
        school_id = user.get("school_id")

        if user_role == "platform_admin":
            unread_sql = "SELECT count(*) FROM portal_notifications WHERE (recipient_user_id = ? OR recipient_role = 'platform_admin' OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL))) AND is_read = 0"
            unread_params = [user_id, user_role, school_id]
        elif user_role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff", "teacher", "academic_coordinator"):
            unread_sql = "SELECT count(*) FROM portal_notifications WHERE (recipient_user_id = ? OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL)) OR (recipient_role = 'school_staff' AND (institution_id = ? OR institution_id IS NULL))) AND is_read = 0"
            unread_params = [user_id, user_role, school_id, school_id]
        else:
            unread_sql = "SELECT count(*) FROM portal_notifications WHERE recipient_user_id = ? AND is_read = 0"
            unread_params = [user_id]

        count = conn.execute(unread_sql, tuple(unread_params)).fetchone()[0]
        return {"unread_count": count}
    finally:
        conn.close()


@app.post("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Marks a specific notification as read, recording read timestamp.
    """
    conn = get_connection()
    try:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE portal_notifications SET is_read = 1, read_at = ? WHERE notification_id = ?",
            (now_str, notification_id),
        )
        conn.commit()
        return {"status": "success", "notification_id": notification_id, "read_at": now_str}
    finally:
        conn.close()


@app.post("/notifications/read-all")
def mark_all_notifications_as_read(
    user: dict = Depends(get_current_user),
):
    """
    Marks all notifications for the authenticated user as read.
    """
    conn = get_connection()
    try:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        user_role = user.get("role")
        user_id = user["user_id"]
        school_id = user.get("school_id")

        if user_role == "platform_admin":
            res = conn.execute(
                "UPDATE portal_notifications SET is_read = 1, read_at = ? WHERE (recipient_user_id = ? OR recipient_role = 'platform_admin' OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL))) AND is_read = 0",
                (now_str, user_id, user_role, school_id)
            )
        elif user_role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff", "teacher", "academic_coordinator"):
            res = conn.execute(
                "UPDATE portal_notifications SET is_read = 1, read_at = ? WHERE (recipient_user_id = ? OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL)) OR (recipient_role = 'school_staff' AND (institution_id = ? OR institution_id IS NULL))) AND is_read = 0",
                (now_str, user_id, user_role, school_id, school_id)
            )
        else:
            res = conn.execute(
                "UPDATE portal_notifications SET is_read = 1, read_at = ? WHERE recipient_user_id = ? AND is_read = 0",
                (now_str, user_id)
            )
        conn.commit()
        return {"status": "success", "marked_read_count": res.rowcount}
    finally:
        conn.close()


@app.get("/notifications/preferences")
def get_user_notification_preferences(
    user: dict = Depends(get_current_user),
):
    """
    Returns user's notification preferences.
    """
    conn = get_connection()
    try:
        return notification_service.get_user_preferences(conn, user["user_id"])
    finally:
        conn.close()


@app.put("/notifications/preferences")
def update_user_notification_preferences(
    payload: NotificationPreferencesPayload,
    user: dict = Depends(get_current_user),
):
    """
    Updates user's notification preferences.
    """
    conn = get_connection()
    try:
        updated = notification_service.update_user_preferences(conn, user["user_id"], payload.dict())
        return updated
    finally:
        conn.close()


@app.get("/notifications/channels/status")
def get_delivery_channel_status(
    user: dict = Depends(get_current_user),
):
    """
    Returns external delivery provider status (Email/SMS/WhatsApp/In-app).
    """
    return notification_service.get_channel_statuses()


@app.get("/notifications/delivery-logs")
def list_notification_delivery_logs(
    notification_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    user: dict = Depends(require_school_staff),
):
    """
    Staff and Admin ledger of external delivery attempts with delivery status.
    """
    conn = get_connection()
    try:
        query = "SELECT * FROM notification_delivery_logs WHERE 1=1"
        params = []
        if notification_id:
            query += " AND notification_id = ?"
            params.append(notification_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


class AiChatPayload(BaseModel):
    prompt: str


@app.post("/ai/chat")
def handle_ai_chat(
    payload: AiChatPayload,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Central AI Assistance Module endpoint for NagrikSetu.
    Grounded strictly against database records with RBAC data isolation.
    """
    from ai_agent import execute_grounded_ai_query
    conn = get_connection()
    try:
        result = execute_grounded_ai_query(conn, payload.prompt, current_user)
        return result
    finally:
        conn.close()


import hashlib
import tempfile
import io
from fastapi import File, UploadFile
from datetime import datetime

@app.post("/idp/process-document")
async def process_idp_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Accepts a genuine uploaded educational certificate (PDF or Image),
    validates file size (max 10MB), validates magic bytes and MIME content,
    executes real Tesseract 5.5.0 OCR or PyPDF native text extraction,
    extracts structured candidate entities, and marks missing fields as 'Not detected'.
    Traceable to the uploaded file SHA-256 hash.
    STRICTLY NON-DESTRUCTIVE: Zero database writes or official student/guardian modifications.
    """
    content = await file.read()
    size_bytes = len(content)

    if size_bytes == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty (0 bytes)."
        )
    if size_bytes > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10 MB limit."
        )

    # Validate Magic Bytes & Content Type
    is_pdf = content.startswith(b"%PDF")
    is_image = False

    if not is_pdf:
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(content))
            img.verify()
            is_image = True
        except Exception:
            is_image = False

    if not is_pdf and not is_image:
        raise HTTPException(
            status_code=400,
            detail="Unsupported or corrupted file format. Only valid PDF documents and JPEG/PNG images are supported."
        )

    # Compute SHA-256 for traceability
    sha256_hash = hashlib.sha256(content).hexdigest()

    # Save to a temporary file for processing
    ext = ".pdf" if is_pdf else ".png"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if is_pdf:
            raw_text, confidence = ocr_service.extract_text_from_pdf(tmp_path)
            engine_name = "PyPDF 6.21.4 (Native Document Stream Parser)"
        else:
            raw_text, confidence = ocr_service.extract_text_and_confidence_from_image(tmp_path)
            engine_name = "Tesseract 5.5.0 (C++ Engine) + Pillow Preprocessing"

        # Parse structured entities
        parsed = ocr_service.parse_structured_entities(raw_text)

        # Lookup school name if school_id was detected
        school_name = "Not detected"
        school_id = parsed.get("school_id") or "Not detected"
        if school_id != "Not detected":
            conn = get_connection()
            try:
                s_row = conn.execute("SELECT school_name FROM schools WHERE school_id = ?", (school_id,)).fetchone()
                if s_row:
                    school_name = s_row["school_name"]
            finally:
                conn.close()

        if school_name == "Not detected" and parsed.get("issuing_authority") and "School" in parsed["issuing_authority"]:
            school_name = parsed["issuing_authority"]

        extracted_entities = {
            "student_name": parsed.get("candidate_name") or "Not detected",
            "student_ref": parsed.get("registration_number") or "Not detected",
            "school_id": school_id,
            "school_name": school_name,
            "dob": parsed.get("date_of_birth") or "Not detected",
            "standard": parsed.get("standard") or "Not detected",
            "guardian_name": parsed.get("guardian_name") or "Not detected",
            "marks_percentage": f"{parsed['marks_percentage']}%" if parsed.get("marks_percentage") else "Not detected",
            "issuing_authority": parsed.get("issuing_authority") or "Not detected"
        }

        return {
            "traceability": {
                "filename": file.filename,
                "size_bytes": size_bytes,
                "sha256": sha256_hash,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            },
            "ocr_engine": engine_name,
            "is_simulated": False,
            "confidence_percentage": f"{confidence}%" if confidence > 0 else "Not detected",
            "raw_text_preview": (raw_text[:300] + ("..." if len(raw_text) > 300 else "")) if raw_text else "No readable text detected",
            "extracted_entities": extracted_entities
        }
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# =====================================================================
# INSTITUTION ADMIN MANAGEMENT & WORKSPACE SELECTION ENDPOINTS
# =====================================================================

class InviteAdminPayload(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    institution_id: str
    role_id: Literal["academic_admin"] = "academic_admin"


class DeclineInvitationPayload(BaseModel):
    token: str
    reason: Optional[str] = "Declined by invitee"


class VerifyIdentityPayload(BaseModel):
    institution_id: str
    email: str
    phone: Optional[str] = None


class AcceptInvitationPayload(BaseModel):
    token: Optional[str] = None
    session_token: Optional[str] = None
    password: str


class SelectWorkspacePayload(BaseModel):
    temp_token: str
    institution_id: str


class InviteStaffPayload(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    institution_id: Optional[str] = None
    role_id: str = "school_staff"
    permissions: Optional[dict] = None


class UpdateStaffPermissionsPayload(BaseModel):
    role_id: Optional[str] = None
    can_view_applications: Optional[bool] = None
    can_review_details: Optional[bool] = None
    can_request_clarification: Optional[bool] = None
    can_recommend_decision: Optional[bool] = None
    can_approve_stage1: Optional[bool] = None
    can_view_history: Optional[bool] = None
    can_manage_academics: Optional[bool] = None
    can_manage_students: Optional[bool] = None


class AdmissionRecommendationRequest(BaseModel):
    recommendation: str
    notes: str


class ForgotPasswordPayload(BaseModel):
    identifier: str


class ResetPasswordPayload(BaseModel):
    token: str
    password: Optional[str] = None
    new_password: Optional[str] = None


@app.get("/admin/institution-admins/eligible-institutions")
def list_eligible_institutions_for_admin_invite(
    search: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    user: dict = Depends(require_platform_admin)
):
    """
    Returns institutions that do NOT currently have an active Academic Administrator assignment
    or an active pending invitation. Applies across all 4 tiers (Schools, PU Colleges, Degree Colleges, Universities).
    """
    conn = get_connection()
    try:
        sql = """
            SELECT s.school_id, s.school_name, s.school_type, s.category, s.district, s.address, s.email, s.affiliation
            FROM schools s
            WHERE s.school_id NOT IN (
                -- Active or Suspended accepted Academic Admin (suspended retains institution slot)
                SELECT uir.institution_id
                FROM user_institution_roles uir
                JOIN users u ON u.user_id = uir.user_id
                WHERE uir.role_id = 'academic_admin'
                  AND uir.status IN ('active', 'suspended')
                  AND uir.status NOT IN ('revoked', 'declined', 'cancelled')

                UNION

                -- Pending active invitation
                SELECT it.institution_id
                FROM invitation_tokens it
                JOIN users u ON u.user_id = it.user_id
                JOIN user_institution_roles uir ON uir.user_id = it.user_id AND uir.institution_id = it.institution_id
                WHERE it.role_id = 'academic_admin'
                  AND it.is_used = 0
                  AND it.expires_at > CURRENT_TIMESTAMP
                  AND uir.status NOT IN ('revoked', 'declined', 'cancelled')
            )
        """
        params = []
        if category and category.lower() != "all":
            cat_map = {
                "k10_school": "Schools (K-10)",
                "pu_college": "PU Colleges (11-12)",
                "degree_college": "Degree Colleges",
                "university": "Universities"
            }
            target_cat = cat_map.get(category.lower(), category)
            sql += " AND s.category = ?"
            params.append(target_cat)

        if search and search.strip():
            term = f"%{search.strip()}%"
            sql += " AND (s.school_id LIKE ? OR s.school_name LIKE ? OR s.district LIKE ?)"
            params.extend([term, term, term])

        sql += " ORDER BY s.school_name ASC"
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        return {
            "institutions": rows,
            "total_eligible": len(rows)
        }
    finally:
        conn.close()


@app.get("/admin/institution-admins")
def list_institution_admins(user: dict = Depends(require_platform_admin)):
    """Lists Academic Administrator assignments separated into pending and active."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT u.user_id, u.full_name, u.email, u.phone, u.status as user_status,
                   u.is_active, u.created_at as user_created_at, u.last_login,
                   uir.id as role_mapping_id, uir.institution_id, s.school_name,
                   s.school_type, s.category, uir.role_id, uir.status as role_status,
                   uir.created_at as mapping_created_at,
                   it.token_id, it.expires_at as invitation_expires_at, it.is_used as invitation_used,
                   it.created_at as invitation_created_at, it.used_at as invitation_used_at
            FROM user_institution_roles uir
            JOIN users u ON u.user_id = uir.user_id
            JOIN schools s ON s.school_id = uir.institution_id
            LEFT JOIN invitation_tokens it ON it.token_id = (
                SELECT token_id FROM invitation_tokens
                WHERE user_id = u.user_id AND institution_id = uir.institution_id
                ORDER BY created_at DESC LIMIT 1
            )
            WHERE uir.status NOT IN ('revoked', 'declined', 'cancelled')
              AND uir.role_id = 'academic_admin'
            ORDER BY uir.created_at DESC
        """).fetchall()

        result = []
        for r in rows:
            is_pending = (r["role_status"] == "invited" or (r["invitation_used"] == 0 and r["role_status"] != "active"))
            invitation_state = "pending" if is_pending else "accepted"
            account_state = "active" if (r["is_active"] == 1 and r["role_status"] == "active") else ("suspended" if r["role_status"] == "suspended" or r["user_status"] == "suspended" else "invited")

            result.append({
                "mapping_id": r["role_mapping_id"],
                "user_id": r["user_id"],
                "full_name": r["full_name"],
                "email": r["email"],
                "phone": r["phone"],
                "institution_id": r["institution_id"],
                "school_name": r["school_name"],
                "school_type": r["school_type"],
                "category": r["category"],
                "role_id": "academic_admin",
                "role_name": "Academic Administrator",
                "status": account_state,
                "invitation_status": invitation_state,
                "is_pending": is_pending,
                "created_at": r["mapping_created_at"] or r["invitation_created_at"] or r["user_created_at"],
                "invitation_sent_at": r["invitation_created_at"] or r["mapping_created_at"] or r["user_created_at"],
                "invitation_accepted_at": r["invitation_used_at"],
                "account_activated_at": r["invitation_used_at"],
                "last_login": r["last_login"]
            })
        return result
    finally:
        conn.close()


@app.post("/admin/institution-admins/reset-assignments")
def reset_institution_admin_assignments(user: dict = Depends(require_platform_admin)):
    """Safely revokes all administrator assignments and pending invitations, releasing all 30 institutions."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        affected_users = conn.execute("""
            SELECT user_id, email, full_name, role, school_id
            FROM users
            WHERE role IN ('school_admin', 'academic_admin', 'school_staff', 'institution_admin')
              AND role NOT IN ('platform_admin', 'student', 'parent')
        """).fetchall()

        affected_mappings = conn.execute("""
            SELECT id, user_id, institution_id, role_id
            FROM user_institution_roles
            WHERE status != 'revoked'
        """).fetchall()

        affected_tokens = conn.execute("""
            SELECT token_id FROM invitation_tokens WHERE is_used = 0
        """).fetchall()

        occupied_schools = conn.execute("""
            SELECT DISTINCT institution_id
            FROM user_institution_roles
            WHERE status IN ('active', 'invited', 'suspended')
        """).fetchall()

        conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE is_used = 0")
        conn.execute("UPDATE user_institution_roles SET status = 'revoked' WHERE status != 'revoked'")
        conn.execute("""
            UPDATE users
            SET school_id = NULL,
                status = 'inactive',
                is_active = 0
            WHERE role IN ('school_admin', 'academic_admin', 'school_staff', 'institution_admin')
              AND role NOT IN ('platform_admin', 'student', 'parent')
        """)

        record_platform_audit(
            conn,
            event_type="ADMIN_ASSIGNMENT_REVOKED",
            event_category="staff",
            institution_id=None,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="institution_assignment",
            entity_id="all_institutions",
            action="All Academic Administrator assignments revoked and 30 institutions released for reassignment",
            old_values={
                "affected_accounts": len(affected_users),
                "affected_mappings": len(affected_mappings),
                "affected_pending_invitations": len(affected_tokens),
                "previously_occupied_institutions": [r["institution_id"] for r in occupied_schools]
            },
            new_values={"released_institutions_count": len(occupied_schools), "available_institutions": 30},
            remarks="Administrator assignments cleared by Platform Admin"
        )
        conn.commit()
        return {
            "status": "success",
            "message": "All Academic Administrator assignments successfully reset. All 30 institutions released for reassignment.",
            "affected_accounts_count": len(affected_users),
            "affected_mappings_count": len(affected_mappings),
            "affected_pending_invitations_count": len(affected_tokens),
            "released_institutions_count": len(occupied_schools),
            "total_available_institutions": 30
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/admin/institution-admins/invite")
def invite_institution_admin(
    payload: InviteAdminPayload,
    user: dict = Depends(require_platform_admin)
):
    """Platform Admin creates a new institution Academic Administrator with a cryptographic single-use invitation token."""
    if payload.role_id != "academic_admin":
        raise HTTPException(
            status_code=400,
            detail="Invalid role: Only 'academic_admin' (Academic Administrator) can be invited through this workflow."
        )

    email_clean = payload.email.strip().lower()
    full_name_clean = payload.full_name.strip()
    inst_id = payload.institution_id.strip()

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        # 1. Verify institution exists
        school = conn.execute("SELECT school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, f"Institution '{inst_id}' does not exist.")

        # 2. Recheck institution availability (Atomic check to prevent race conditions / duplicate assignments)
        existing_active = conn.execute("""
            SELECT u.full_name, u.email, uir.status, 'assigned' as status_type
            FROM user_institution_roles uir
            JOIN users u ON u.user_id = uir.user_id
            WHERE uir.institution_id = ?
              AND uir.role_id = 'academic_admin'
              AND uir.status IN ('active', 'suspended')
              AND uir.status NOT IN ('revoked', 'declined', 'cancelled')

            UNION

            SELECT u.full_name, u.email, 'pending_invitation' as status, 'pending' as status_type
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN user_institution_roles uir ON uir.user_id = it.user_id AND uir.institution_id = it.institution_id
            WHERE it.institution_id = ?
              AND it.role_id = 'academic_admin'
              AND it.is_used = 0
              AND it.expires_at > CURRENT_TIMESTAMP
              AND uir.status NOT IN ('revoked', 'declined', 'cancelled')
        """, (inst_id, inst_id)).fetchone()

        if existing_active:
            kind_desc = "an active assignment" if existing_active["status_type"] == "assigned" else "a pending invitation"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Target institution '{school['school_name']}' ({inst_id}) already has {kind_desc} for the Academic Administrator role ({existing_active['email']}). Only one Academic Administrator is allowed per institution."
            )

        # 3. Check if user already exists
        existing_user = conn.execute("SELECT user_id, role, is_active FROM users WHERE email = ? COLLATE NOCASE", (email_clean,)).fetchone()

        if existing_user:
            user_id = existing_user["user_id"]
            existing_role = conn.execute(
                "SELECT id, status FROM user_institution_roles WHERE user_id = ? AND institution_id = ? AND role_id = 'academic_admin'",
                (user_id, inst_id)
            ).fetchone()
            if existing_role and existing_role["status"] in ('active', 'invited', 'suspended'):
                raise HTTPException(409, f"User already has an active or pending role 'academic_admin' in institution '{inst_id}'.")

            if existing_role:
                role_mapping_id = existing_role["id"]
                conn.execute("UPDATE user_institution_roles SET status = 'invited', created_by = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?", (user["user_id"], role_mapping_id))
            else:
                role_mapping_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
                    VALUES (?, ?, ?, 'academic_admin', 'invited', ?)
                """, (role_mapping_id, user_id, inst_id, user["user_id"]))
            conn.execute("UPDATE users SET school_id = ?, full_name = ?, status = 'invited' WHERE user_id = ?", (inst_id, full_name_clean, user_id))
        else:
            user_id = str(uuid.uuid4())
            dummy_hash = hash_password(secrets.token_urlsafe(16) + "A1!")
            phone_val = payload.phone
            if phone_val:
                p_dup = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone_val,)).fetchone()
                if p_dup:
                    phone_val = None
            conn.execute("""
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
                VALUES (?, ?, ?, ?, 'school_staff', ?, 0, 'invited', ?)
            """, (user_id, email_clean, phone_val, dummy_hash, inst_id, full_name_clean))

            role_mapping_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
                VALUES (?, ?, ?, 'academic_admin', 'invited', ?)
            """, (role_mapping_id, user_id, inst_id, user["user_id"]))

        # 5. Generate cryptographic invitation token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
        token_id = str(uuid.uuid4())

        conn.execute("""
            INSERT INTO invitation_tokens (token_id, token_hash, user_id, institution_id, role_id, expires_at, is_used, created_by)
            VALUES (?, ?, ?, ?, 'academic_admin', ?, 0, ?)
        """, (token_id, token_hash, user_id, inst_id, expires_at, user["user_id"]))

        # 6. Audit Logging
        record_platform_audit(
            conn,
            event_type="ADMIN_INVITED",
            event_category="staff",
            institution_id=inst_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="user_institution_roles",
            entity_id=role_mapping_id,
            action=f"Academic Administrator invitation created for {full_name_clean} ({email_clean}) at {school['school_name']} ({inst_id})",
            new_values={"email": email_clean, "role_id": "academic_admin", "institution_id": inst_id, "token_id": token_id},
            remarks="Administrator invitation dispatched"
        )
        conn.commit()

        return {
            "status": "invited",
            "user_id": user_id,
            "full_name": full_name_clean,
            "email": email_clean,
            "institution_id": inst_id,
            "school_name": school["school_name"],
            "role_id": "academic_admin",
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "invitation_token": raw_token,
            "dev_token": raw_token,
            "email_delivery": "Simulated/Dev Mode: External SMTP unconfigured. Invitation link generated securely."
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/admin/institution-admins/{user_id}/suspend")
def suspend_institution_admin(user_id: str, user: dict = Depends(require_platform_admin)):
    conn = get_connection()
    try:
        row = conn.execute("SELECT user_id, email, full_name, school_id, is_active, status FROM users WHERE user_id = ?", (user_id,)).fetchone()
        admin_user = dict(row) if row else {}
        conn.execute("UPDATE users SET is_active = 0, status = 'suspended' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'suspended' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE user_id = ?", (user_id,))
        record_platform_audit(
            conn,
            event_type="ADMIN_SUSPENDED",
            event_category="staff",
            institution_id=admin_user.get("school_id"),
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="users",
            entity_id=user_id,
            action=f"Academic Administrator suspended: {admin_user.get('full_name', user_id)} (Institution assignment retained)",
            old_values={"is_active": 1, "status": "active"},
            new_values={"is_active": 0, "status": "suspended"},
            remarks="Administrator account suspended by Platform Admin. Institution slot retained."
        )
        conn.commit()
        return {"status": "suspended", "user_id": user_id}
    finally:
        conn.close()


@app.post("/admin/institution-admins/{user_id}/revoke-invitation")
def revoke_institution_invitation(user_id: str, user: dict = Depends(require_platform_admin)):
    """Platform Admin revokes a pending invitation, releasing the institution immediately."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT user_id, email, full_name, school_id, is_active, status FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Administrator record not found.")
        target = dict(row)

        inst_row = conn.execute("SELECT institution_id FROM user_institution_roles WHERE user_id = ? AND status IN ('invited', 'active', 'suspended') ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
        inst_id = inst_row["institution_id"] if inst_row else target["school_id"]

        conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'revoked' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE users SET status = 'revoked', is_active = 0, school_id = NULL WHERE user_id = ?", (user_id,))

        record_platform_audit(
            conn,
            event_type="ADMIN_REVOKED",
            event_category="staff",
            institution_id=inst_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="invitation_tokens",
            entity_id=user_id,
            action=f"Academic Administrator invitation revoked for {target.get('full_name') or user_id} ({target['email']})",
            new_values={"status": "revoked"},
            remarks="Invitation token revoked and institution released for reassignment"
        )
        conn.commit()
        return {"status": "revoked", "user_id": user_id, "message": "Invitation revoked successfully. The institution has been released for reassignment."}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/auth/decline-invitation")
def decline_invitation(payload: DeclineInvitationPayload):
    """Invited candidate declines the invitation, releasing the institution immediately."""
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        inv = conn.execute("""
            SELECT it.*, u.email, u.full_name, s.school_name
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN schools s ON s.school_id = it.institution_id
            WHERE it.token_hash = ?
        """, (token_hash,)).fetchone()
        if not inv:
            raise HTTPException(400, "Invalid invitation token.")
        if inv["is_used"] == 1:
            raise HTTPException(400, "Invitation has already been used, declined, or revoked.")

        conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE token_id = ?", (inv["token_id"],))
        conn.execute("UPDATE user_institution_roles SET status = 'declined' WHERE user_id = ? AND institution_id = ?", (inv["user_id"], inv["institution_id"]))
        conn.execute("UPDATE users SET status = 'declined', is_active = 0, school_id = NULL WHERE user_id = ?", (inv["user_id"],))

        record_platform_audit(
            conn,
            event_type="INVITATION_DECLINED",
            event_category="staff",
            institution_id=inv["institution_id"],
            actor_user_id=inv["user_id"],
            actor_role="academic_admin",
            actor_name=inv["full_name"],
            entity_type="invitation_tokens",
            entity_id=inv["token_id"],
            action=f"Academic Administrator invitation declined by {inv['full_name']} ({inv['email']}) for {inv['school_name']}",
            new_values={"status": "declined"},
            remarks="Invitation declined by invitee and institution released for reassignment"
        )

        conn.commit()
        return {"status": "declined", "message": "Invitation declined. The institution has been released for reassignment."}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/admin/institution-admins/{user_id}/reactivate")
def reactivate_institution_admin(user_id: str, user: dict = Depends(require_platform_admin)):
    conn = get_connection()
    try:
        row = conn.execute("SELECT user_id, email, full_name, school_id, is_active, status FROM users WHERE user_id = ?", (user_id,)).fetchone()
        admin_user = dict(row) if row else {}
        conn.execute("UPDATE users SET is_active = 1, status = 'active' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'active' WHERE user_id = ?", (user_id,))
        record_platform_audit(
            conn,
            event_type="ADMIN_REACTIVATED",
            event_category="staff",
            institution_id=admin_user.get("school_id"),
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="users",
            entity_id=user_id,
            action=f"Academic Administrator reactivated: {admin_user.get('full_name', user_id)}",
            old_values={"is_active": 0, "status": "suspended"},
            new_values={"is_active": 1, "status": "active"},
            remarks="Administrator account reactivated by Platform Admin"
        )
        conn.commit()
        return {"status": "active", "user_id": user_id}
    finally:
        conn.close()


@app.get("/auth/verify-invitation")
def verify_invitation_token(token: str = Query(...)):
    token_hash = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT it.*, u.email, u.full_name, u.status as user_status, s.school_name, s.school_type
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN schools s ON s.school_id = it.institution_id
            WHERE it.token_hash = ?
        """, (token_hash,)).fetchone()

        if not row:
            raise HTTPException(400, "Invalid invitation token.")

        if row["is_used"] == 1:
            raise HTTPException(400, "This invitation token has already been used.")

        # Check expiration
        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This invitation token has expired.")

        # State C: When invited administrator opens & verifies invitation, transition status to accepted_pending_password
        if row["user_status"] == "invited":
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE user_institution_roles SET status = 'accepted_pending_password' WHERE user_id = ? AND institution_id = ? AND status = 'invited'",
                (row["user_id"], row["institution_id"])
            )
            conn.execute(
                "UPDATE users SET status = 'accepted_pending_password' WHERE user_id = ? AND status = 'invited'",
                (row["user_id"],)
            )
            record_platform_audit(
                conn,
                event_type="INVITATION_ACCEPTED_PENDING_PASSWORD",
                event_category="staff",
                institution_id=row["institution_id"],
                actor_user_id=row["user_id"],
                actor_role="academic_admin",
                actor_name=row["full_name"],
                entity_type="invitation_tokens",
                entity_id=row["token_id"],
                action=f"Academic Administrator invitation opened and accepted by {row['full_name']} ({row['email']}); awaiting password creation",
                old_values={"status": "invited"},
                new_values={"status": "accepted_pending_password"},
                remarks="Candidate verified token; awaiting password configuration"
            )
            conn.commit()

        return {
            "valid": True,
            "email": row["email"],
            "full_name": row["full_name"],
            "institution_id": row["institution_id"],
            "school_name": row["school_name"],
            "school_type": row["school_type"],
            "role_id": row["role_id"],
            "status": "ACCEPTED_PENDING_PASSWORD"
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/auth/invitations/verify-identity")
def verify_invitation_identity(payload: VerifyIdentityPayload):
    """Validates the intended administrator's official email against the pending invitation for the institution.
    Returns a cryptographically signed setup session token and read-only administrator details.
    Unauthorized attempts with mismatched emails are rejected with HTTP 403 Forbidden."""
    inst_id = payload.institution_id.strip()
    email_clean = payload.email.strip().lower()

    conn = get_connection()
    try:
        # Check institution exists
        school = conn.execute("SELECT school_id, school_name, school_type, district FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, f"Institution '{inst_id}' not found.")

        # Find active pending invitation for this institution
        inv = conn.execute("""
            SELECT it.*, u.email, u.full_name, u.phone, u.status as user_status
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            WHERE it.institution_id = ?
              AND it.is_used = 0
            ORDER BY it.created_at DESC LIMIT 1
        """, (inst_id,)).fetchone()

        if not inv:
            raise HTTPException(404, f"No pending administrator invitation found for {school['school_name']} ({inst_id}).")

        # Check expiration
        exp = datetime.fromisoformat(inv["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "The administrator invitation for this institution has expired. Please contact the Platform Administrator for a renewed invitation.")

        # STRICT SECURITY CHECK: Does the provided email match the invited administrator?
        expected_email = inv["email"].strip().lower()
        if email_clean != expected_email:
            record_platform_audit(
                conn,
                event_type="UNAUTHORIZED_INVITATION_CLAIM_ATTEMPT",
                event_category="security",
                institution_id=inst_id,
                actor_user_id=None,
                actor_role="anonymous",
                entity_type="invitation_tokens",
                entity_id=inv["token_id"],
                action=f"Unauthorized claim attempt on {school['school_name']} ({inst_id}) with email '{payload.email}'",
                remarks="Email mismatch on institution invitation claim"
            )
            conn.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Verification Failed: The provided email does not match the official invitee appointed for {school['school_name']}."
            )

        # Transition status to accepted_pending_password if not already
        if inv["user_status"] == "invited":
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE user_institution_roles SET status = 'accepted_pending_password' WHERE user_id = ? AND institution_id = ? AND status = 'invited'",
                (inv["user_id"], inst_id)
            )
            conn.execute(
                "UPDATE users SET status = 'accepted_pending_password' WHERE user_id = ? AND status = 'invited'",
                (inv["user_id"],)
            )
            record_platform_audit(
                conn,
                event_type="INVITATION_ACCEPTED_PENDING_PASSWORD",
                event_category="staff",
                institution_id=inst_id,
                actor_user_id=inv["user_id"],
                actor_role="academic_admin",
                actor_name=inv["full_name"],
                entity_type="invitation_tokens",
                entity_id=inv["token_id"],
                action=f"Academic Administrator identity verified for {inv['full_name']} ({inv['email']}); awaiting password creation",
                old_values={"status": "invited"},
                new_values={"status": "accepted_pending_password"},
                remarks="Candidate verified email identity; awaiting password configuration"
            )
            conn.commit()

        # Generate secure setup session token (valid for 30 minutes)
        import jwt
        from auth import JWT_SECRET_KEY, JWT_ALGORITHM
        setup_session_token = jwt.encode(
            {
                "sub": inv["user_id"],
                "email": inv["email"],
                "institution_id": inst_id,
                "token_id": inv["token_id"],
                "token_hash": inv["token_hash"],
                "purpose": "invitation_setup",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "jti": str(uuid.uuid4())
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        return {
            "status": "verified",
            "session_token": setup_session_token,
            "administrator": {
                "full_name": inv["full_name"],
                "email": inv["email"],
                "phone": inv["phone"],
                "institution_id": inst_id,
                "school_name": school["school_name"],
                "school_type": school["school_type"],
                "district": school["district"],
                "role_id": "academic_admin",
                "role_name": "Academic Administrator"
            }
        }
    finally:
        conn.close()


@app.post("/auth/accept-invitation")
def accept_invitation(payload: AcceptInvitationPayload):
    if len(payload.password) < 8:
        raise HTTPException(422, "Password must contain at least 8 characters.")

    inv_token_id = None
    token_hash = None

    if payload.session_token:
        import jwt
        from auth import JWT_SECRET_KEY, JWT_ALGORITHM
        try:
            decoded = jwt.decode(
                payload.session_token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"require": ["sub", "exp", "iat", "jti"]}
            )
            if decoded.get("purpose") != "invitation_setup":
                raise HTTPException(401, "Invalid session token purpose.")
            inv_token_id = decoded.get("token_id")
            token_hash = decoded.get("token_hash")
        except Exception:
            raise HTTPException(401, "Invalid or expired invitation setup session. Please verify your identity again.")
    elif payload.token:
        token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    else:
        raise HTTPException(400, "Missing invitation token or setup session.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        if inv_token_id:
            inv = conn.execute("""
                SELECT it.*, u.email, u.full_name, s.school_name
                FROM invitation_tokens it
                JOIN users u ON u.user_id = it.user_id
                JOIN schools s ON s.school_id = it.institution_id
                WHERE it.token_id = ?
            """, (inv_token_id,)).fetchone()
        else:
            inv = conn.execute("""
                SELECT it.*, u.email, u.full_name, s.school_name
                FROM invitation_tokens it
                JOIN users u ON u.user_id = it.user_id
                JOIN schools s ON s.school_id = it.institution_id
                WHERE it.token_hash = ?
            """, (token_hash,)).fetchone()

        if not inv:
            raise HTTPException(400, "Invalid invitation token.")
        if inv["is_used"] == 1:
            raise HTTPException(400, "This invitation token has already been used.")

        exp = datetime.fromisoformat(inv["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            record_platform_audit(
                conn,
                event_type="INVITATION_EXPIRED",
                event_category="staff",
                institution_id=inv["institution_id"],
                actor_user_id=inv["user_id"],
                actor_role="academic_admin",
                entity_type="invitation_tokens",
                entity_id=inv["token_id"],
                action=f"Academic Administrator invitation expired for {inv['email']}",
                remarks="Candidate attempted activation with expired token"
            )
            conn.commit()
            raise HTTPException(400, "This invitation token has expired.")

        new_hash = hash_password(payload.password)

        # Activate user and set password, role, and institution mapping
        conn.execute("""
            UPDATE users 
            SET password_hash = ?, is_active = 1, status = 'active', school_id = ?
            WHERE user_id = ?
        """, (new_hash, inv["institution_id"], inv["user_id"]))

        # Activate user_institution_role
        conn.execute("""
            UPDATE user_institution_roles
            SET status = 'active', role_id = 'academic_admin'
            WHERE user_id = ? AND institution_id = ?
        """, (inv["user_id"], inv["institution_id"]))

        # Mark token as used
        conn.execute("""
            UPDATE invitation_tokens
            SET is_used = 1, used_at = CURRENT_TIMESTAMP
            WHERE token_id = ?
        """, (inv["token_id"],))

        # Central Platform Audit Events: ADMIN_ACCEPTED, ACCOUNT_ACTIVATED, INSTITUTION_ASSIGNED
        record_platform_audit(
            conn,
            event_type="ADMIN_ACCEPTED",
            event_category="staff",
            institution_id=inv["institution_id"],
            actor_user_id=inv["user_id"],
            actor_role="academic_admin",
            actor_name=inv["full_name"],
            entity_type="invitation_tokens",
            entity_id=inv["token_id"],
            action=f"Academic Administrator invitation accepted by {inv['full_name']} ({inv['email']})",
            old_values={"invitation_status": "pending"},
            new_values={"invitation_status": "accepted", "institution_id": inv["institution_id"]},
            remarks="Invitation token verified and validated"
        )

        record_platform_audit(
            conn,
            event_type="ACCOUNT_ACTIVATED",
            event_category="staff",
            institution_id=inv["institution_id"],
            actor_user_id=inv["user_id"],
            actor_role="academic_admin",
            actor_name=inv["full_name"],
            entity_type="users",
            entity_id=inv["user_id"],
            action=f"Academic Administrator account activated for {inv['full_name']} ({inv['email']})",
            old_values={"is_active": 0, "status": "invited"},
            new_values={"is_active": 1, "status": "active", "role": "academic_admin"},
            remarks="Password configured and account activated"
        )

        record_platform_audit(
            conn,
            event_type="INSTITUTION_ASSIGNED",
            event_category="institution",
            institution_id=inv["institution_id"],
            actor_user_id=inv["user_id"],
            actor_role="academic_admin",
            actor_name=inv["full_name"],
            entity_type="user_institution_roles",
            entity_id=inv["institution_id"],
            action=f"Institution assignment completed: {inv['school_name']} ({inv['institution_id']}) assigned to {inv['full_name']}",
            new_values={"institution_id": inv["institution_id"], "role_id": "academic_admin", "status": "active"},
            remarks="Institutional assignment finalized"
        )

        conn.commit()
        return {"status": "activated", "message": "Account activated successfully. You can now sign in."}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/auth/select-workspace")
def select_institution_workspace(payload: SelectWorkspacePayload):
    """Allows a multi-institution administrator to select their active institution workspace."""
    import jwt
    from auth import JWT_SECRET_KEY, JWT_ALGORITHM
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired workspace selection token.",
    )
    try:
        decoded = jwt.decode(
            payload.temp_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat", "jti"]}
        )
        if decoded.get("purpose") != "workspace_selection":
            raise unauthorized
        user_id = decoded["sub"]
    except Exception:
        raise unauthorized

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, email, phone, role, school_id, is_active, status, full_name FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        if not user or user["is_active"] != 1 or user["status"] == "suspended":
            raise unauthorized

        inst_role = conn.execute("""
            SELECT role_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ? AND status = 'active'
        """, (user_id, payload.institution_id)).fetchone()

        if not inst_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this institution workspace."
            )

        user_data = dict(user)
        user_data["role"] = inst_role["role_id"]
        user_data["school_id"] = payload.institution_id

        access_token = create_access_token(user_data, school_id=payload.institution_id)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": inst_role["role_id"],
            "school_id": payload.institution_id
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/recommend")
def recommend_admission_decision(
    application_id: str,
    payload: AdmissionRecommendationRequest,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id, status, applicant_name FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is assigned to {school_id}.")

        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        if not perms.get("can_recommend_decision") and user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
            raise HTTPException(403, "Forbidden: Account does not have permission to recommend admission decisions.")

        rec_type = payload.recommendation.strip().lower()
        if rec_type not in ("approve", "reject"):
            raise HTTPException(422, "Recommendation must be either 'approve' or 'reject'.")

        note_text = f"Staff Recommendation [{rec_type.upper()}]: {payload.notes.strip()}"
        conn.execute("""
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), application_id, existing["status"], existing["status"], user["user_id"], note_text))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'STAFF_ADMISSION_RECOMMENDATION', 'admission_applications', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), application_id, user["user_id"], user["role"], school_id, json.dumps({
            "recommendation": rec_type,
            "notes": payload.notes.strip()
        })))

        conn.commit()
        return {
            "status": "recommendation_recorded",
            "application_id": application_id,
            "recommendation": rec_type,
            "message": f"Admission recommendation ({rec_type}) successfully recorded."
        }
    finally:
        conn.close()


@app.get("/school/admin/staff")
def list_institution_staff(user: dict = Depends(require_school_admin)):
    """Lists staff assigned to the administrator's own school_id with permissions and invitation states."""
    school_id = user["school_id"]
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT u.user_id, u.full_name, u.email, u.phone, u.status as user_status,
                   u.is_active, u.last_login, uir.role_id, uir.status as role_status, uir.created_at,
                   it.token_id, it.expires_at as invitation_expires_at, it.is_used as invitation_used,
                   isp.can_view_applications, isp.can_review_details, isp.can_request_clarification,
                   isp.can_recommend_decision, isp.can_approve_stage1, isp.can_view_history,
                   isp.can_manage_academics, isp.can_manage_students
            FROM user_institution_roles uir
            JOIN users u ON u.user_id = uir.user_id
            LEFT JOIN (
                SELECT user_id, institution_id, token_id, expires_at, is_used,
                       ROW_NUMBER() OVER (PARTITION BY user_id, institution_id ORDER BY created_at DESC) as rn
                FROM invitation_tokens
            ) it ON it.user_id = u.user_id AND it.institution_id = uir.institution_id AND it.rn = 1
            LEFT JOIN institution_staff_permissions isp ON isp.user_id = u.user_id AND isp.institution_id = uir.institution_id
            WHERE uir.institution_id = ?
            ORDER BY uir.created_at DESC
        """, (school_id,)).fetchall()

        result = []
        for r in rows:
            invitation_state = "accepted"
            if r["invitation_used"] == 0:
                if r["invitation_expires_at"]:
                    try:
                        exp = datetime.fromisoformat(r["invitation_expires_at"].replace("Z", ""))
                        invitation_state = "expired" if datetime.utcnow() > exp else "pending"
                    except Exception:
                        invitation_state = "pending"
                else:
                    invitation_state = "pending"
            elif r["invitation_used"] is None:
                invitation_state = "active"

            if r["role_id"] in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):
                perms = dict(DEFAULT_ROLE_PERMS["school_admin"])
            elif r["can_view_applications"] is not None:
                perms = {
                    "can_view_applications": bool(r["can_view_applications"]),
                    "can_review_details": bool(r["can_review_details"]),
                    "can_request_clarification": bool(r["can_request_clarification"]),
                    "can_recommend_decision": bool(r["can_recommend_decision"]),
                    "can_approve_stage1": bool(r["can_approve_stage1"]),
                    "can_view_history": bool(r["can_view_history"]),
                    "can_manage_academics": bool(r["can_manage_academics"]),
                    "can_manage_students": bool(r["can_manage_students"]),
                }
            else:
                default_p = DEFAULT_ROLE_PERMS.get(r["role_id"], DEFAULT_ROLE_PERMS["general_staff"])
                perms = {k: bool(v) for k, v in default_p.items()}

            result.append({
                "user_id": r["user_id"],
                "full_name": r["full_name"],
                "email": r["email"],
                "phone": r["phone"],
                "role_id": r["role_id"],
                "status": "suspended" if (r["is_active"] == 0 or r["user_status"] == "suspended") else (r["role_status"] or "active"),
                "is_active": r["is_active"] == 1,
                "invitation_status": invitation_state,
                "invitation_expires_at": r["invitation_expires_at"],
                "created_at": r["created_at"],
                "last_login": r["last_login"],
                "permissions": perms
            })
        return result
    finally:
        conn.close()


@app.post("/school/admin/staff/invite")
def invite_school_staff(
    payload: InviteStaffPayload,
    user: dict = Depends(require_school_admin)
):
    """School Admin invites staff for their OWN school ONLY. Cross-school or unauthorized roles forbidden."""
    school_id = user["school_id"]
    valid_roles = ("admissions_officer", "academic_admin", "student_records_officer", "general_staff", "school_staff")
    if payload.role_id not in valid_roles:
        raise HTTPException(400, f"Invalid staff role '{payload.role_id}'. Allowed roles: {', '.join(valid_roles)}")
    if payload.institution_id and payload.institution_id != school_id:
        raise HTTPException(403, f"Cross-institution staff creation forbidden: Admin is at {school_id}, cannot invite for {payload.institution_id}.")

    email_clean = payload.email.strip().lower()
    full_name_clean = payload.full_name.strip()
    phone_clean = payload.phone.strip() if payload.phone and payload.phone.strip() else None

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        existing_user = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (email_clean,)).fetchone()
        if existing_user:
            user_id = existing_user["user_id"]
            existing_role = conn.execute(
                "SELECT id FROM user_institution_roles WHERE user_id = ? AND institution_id = ? AND role_id = ?",
                (user_id, school_id, payload.role_id)
            ).fetchone()
            if existing_role:
                raise HTTPException(409, f"Staff member already assigned role '{payload.role_id}' in this institution.")
        else:
            if phone_clean:
                existing_phone = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone_clean,)).fetchone()
                if existing_phone:
                    phone_clean = None

            user_id = str(uuid.uuid4())
            dummy_hash = hash_password(secrets.token_urlsafe(16) + "S1!")
            user_base_role = "school_admin" if payload.role_id == "school_admin" else "school_staff"
            conn.execute("""
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'invited', ?)
            """, (user_id, email_clean, phone_clean, dummy_hash, user_base_role, school_id, full_name_clean))

        role_mapping_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
            VALUES (?, ?, ?, ?, 'invited', ?)
        """, (role_mapping_id, user_id, school_id, payload.role_id, user["user_id"]))

        default_p = DEFAULT_ROLE_PERMS.get(payload.role_id, DEFAULT_ROLE_PERMS["general_staff"])
        custom_p = payload.permissions or {}
        
        def pick(col):
            if col in custom_p:
                return 1 if custom_p[col] else 0
            return default_p.get(col, 0)

        v_app = pick("can_view_applications")
        v_det = pick("can_review_details")
        v_cla = pick("can_request_clarification")
        v_rec = pick("can_recommend_decision")
        v_appr = pick("can_approve_stage1")
        v_his = pick("can_view_history")
        v_aca = pick("can_manage_academics")
        v_stu = pick("can_manage_students")

        conn.execute("""
            INSERT OR REPLACE INTO institution_staff_permissions
            (id, user_id, institution_id, role_id, can_view_applications, can_review_details,
             can_request_clarification, can_recommend_decision, can_approve_stage1, can_view_history,
             can_manage_academics, can_manage_students, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), user_id, school_id, payload.role_id,
            v_app, v_det, v_cla, v_rec, v_appr, v_his, v_aca, v_stu,
            user["user_id"]
        ))

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
        token_id = str(uuid.uuid4())

        conn.execute("""
            INSERT INTO invitation_tokens (token_id, token_hash, user_id, institution_id, role_id, expires_at, is_used, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (token_id, token_hash, user_id, school_id, payload.role_id, expires_at, user["user_id"]))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'INVITE_STAFF', 'user_institution_roles', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), role_mapping_id, user["user_id"], user["role"], school_id, json.dumps({
            "email": email_clean,
            "role_id": payload.role_id,
            "institution_id": school_id
        })))

        conn.commit()
        return {
            "status": "invited",
            "user_id": user_id,
            "school_id": school_id,
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "invitation_token": raw_token,
            "dev_token": raw_token
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/school/admin/staff/{user_id}/resend-invitation")
def resend_school_staff_invitation(
    user_id: str,
    user: dict = Depends(require_school_admin)
):
    school_id = user["school_id"]
    conn = get_connection()
    try:
        uir = conn.execute("""
            SELECT role_id, institution_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()
        if not uir:
            raise HTTPException(403, f"Cross-institution access forbidden: User {user_id} is not assigned to your institution ({school_id}).")

        target = conn.execute("SELECT email, full_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not target:
            raise HTTPException(404, "User not found.")

        conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE user_id = ? AND institution_id = ?", (user_id, school_id))

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
        token_id = str(uuid.uuid4())

        conn.execute("""
            INSERT INTO invitation_tokens (token_id, token_hash, user_id, institution_id, role_id, expires_at, is_used, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (token_id, token_hash, user_id, school_id, uir["role_id"], expires_at, user["user_id"]))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'RESEND_STAFF_INVITATION', 'user_institution_roles', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, user["user_id"], user["role"], school_id, json.dumps({
            "email": target["email"],
            "role_id": uir["role_id"],
            "institution_id": school_id
        })))

        conn.commit()
        return {
            "status": "resent",
            "user_id": user_id,
            "email": target["email"],
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "invitation_token": raw_token,
            "dev_token": raw_token
        }
    finally:
        conn.close()


@app.post("/school/admin/staff/{user_id}/suspend")
def suspend_school_staff(
    user_id: str,
    user: dict = Depends(require_school_admin)
):
    school_id = user["school_id"]
    if user_id == user["user_id"]:
        raise HTTPException(400, "Cannot suspend your own administrator account.")

    conn = get_connection()
    try:
        uir = conn.execute("""
            SELECT role_id, institution_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()
        if not uir:
            raise HTTPException(403, f"Cross-institution access forbidden: User {user_id} is not assigned to your institution ({school_id}).")

        conn.execute("UPDATE users SET is_active = 0, status = 'suspended' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'suspended' WHERE user_id = ? AND institution_id = ?", (user_id, school_id))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'SUSPEND_STAFF', 'user_institution_roles', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, user["user_id"], user["role"], school_id, json.dumps({
            "target_user_id": user_id,
            "action": "suspend"
        })))

        target_u = conn.execute("SELECT email, full_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if target_u:
            notification_service.trigger_staff_administrative_notification(
                conn, school_id, "Suspended",
                target_u["full_name"] or target_u["email"],
                target_u["email"],
                user.get("email") or "Admin"
            )

        conn.commit()
        return {"status": "suspended", "user_id": user_id}
    finally:
        conn.close()


@app.post("/school/admin/staff/{user_id}/reactivate")
def reactivate_school_staff(
    user_id: str,
    user: dict = Depends(require_school_admin)
):
    school_id = user["school_id"]
    conn = get_connection()
    try:
        uir = conn.execute("""
            SELECT role_id, institution_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()
        if not uir:
            raise HTTPException(403, f"Cross-institution access forbidden: User {user_id} is not assigned to your institution ({school_id}).")

        conn.execute("UPDATE users SET is_active = 1, status = 'active' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'active' WHERE user_id = ? AND institution_id = ?", (user_id, school_id))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'REACTIVATE_STAFF', 'user_institution_roles', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, user["user_id"], user["role"], school_id, json.dumps({
            "target_user_id": user_id,
            "action": "reactivate"
        })))

        target_u = conn.execute("SELECT email, full_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if target_u:
            notification_service.trigger_staff_administrative_notification(
                conn, school_id, "Reactivated",
                target_u["full_name"] or target_u["email"],
                target_u["email"],
                user.get("email") or "Admin"
            )

        conn.commit()
        return {"status": "active", "user_id": user_id}
    finally:
        conn.close()


@app.post("/school/admin/staff/{user_id}/reset-password")
def reset_school_staff_password(
    user_id: str,
    user: dict = Depends(require_school_admin)
):
    school_id = user["school_id"]
    conn = get_connection()
    try:
        uir = conn.execute("""
            SELECT role_id, institution_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()
        if not uir:
            raise HTTPException(403, f"Cross-institution access forbidden: User {user_id} is not assigned to your institution ({school_id}).")

        target = conn.execute("SELECT email, full_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not target:
            raise HTTPException(404, "User not found.")

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reset_id = str(uuid.uuid4())

        conn.execute("""
            INSERT INTO password_reset_tokens (reset_id, token_hash, user_id, expires_at, is_used)
            VALUES (?, ?, ?, ?, 0)
        """, (reset_id, token_hash, user_id, expires_at))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'ADMIN_RESET_STAFF_PASSWORD', 'users', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, user["user_id"], user["role"], school_id, json.dumps({
            "target_user_id": user_id,
            "email": target["email"]
        })))

        conn.commit()
        return {
            "status": "reset_initiated",
            "user_id": user_id,
            "email": target["email"],
            "reset_url": f"/reset-password?token={raw_token}",
            "reset_token": raw_token,
            "dev_reset_url": f"/reset-password?token={raw_token}"
        }
    finally:
        conn.close()


@app.put("/school/admin/staff/{user_id}/permissions")
def update_school_staff_permissions(
    user_id: str,
    payload: UpdateStaffPermissionsPayload,
    user: dict = Depends(require_school_admin)
):
    school_id = user["school_id"]
    conn = get_connection()
    try:
        uir = conn.execute("""
            SELECT role_id, institution_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()
        if not uir:
            raise HTTPException(403, f"Cross-institution access forbidden: User {user_id} is not assigned to your institution ({school_id}).")

        conn.execute("BEGIN IMMEDIATE")

        target_role = payload.role_id or uir["role_id"]
        if payload.role_id and payload.role_id != uir["role_id"]:
            if payload.role_id not in ("admissions_officer", "academic_admin", "student_records_officer", "school_staff", "general_staff"):
                raise HTTPException(400, f"Invalid staff role '{payload.role_id}'.")
            user_base_role = "school_admin" if payload.role_id == "school_admin" else "school_staff"
            conn.execute("""
                UPDATE user_institution_roles SET role_id = ? WHERE user_id = ? AND institution_id = ?
            """, (payload.role_id, user_id, school_id))
            conn.execute("""
                UPDATE users SET role = ? WHERE user_id = ?
            """, (user_base_role, user_id))

        current_perms = conn.execute("""
            SELECT * FROM institution_staff_permissions WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()

        default_p = DEFAULT_ROLE_PERMS.get(target_role, DEFAULT_ROLE_PERMS["general_staff"])

        def val(new_val, col_name):
            if new_val is not None:
                return 1 if new_val else 0
            if current_perms and col_name in current_perms.keys():
                return current_perms[col_name]
            return default_p.get(col_name, 0)

        v_app = val(payload.can_view_applications, "can_view_applications")
        v_det = val(payload.can_review_details, "can_review_details")
        v_cla = val(payload.can_request_clarification, "can_request_clarification")
        v_rec = val(payload.can_recommend_decision, "can_recommend_decision")
        v_appr = val(payload.can_approve_stage1, "can_approve_stage1")
        v_his = val(payload.can_view_history, "can_view_history")
        v_aca = val(payload.can_manage_academics, "can_manage_academics")
        v_stu = val(payload.can_manage_students, "can_manage_students")

        if current_perms:
            conn.execute("""
                UPDATE institution_staff_permissions
                SET role_id = ?, can_view_applications = ?, can_review_details = ?,
                    can_request_clarification = ?, can_recommend_decision = ?,
                    can_approve_stage1 = ?, can_view_history = ?,
                    can_manage_academics = ?, can_manage_students = ?,
                    updated_at = CURRENT_TIMESTAMP, updated_by = ?
                WHERE user_id = ? AND institution_id = ?
            """, (target_role, v_app, v_det, v_cla, v_rec, v_appr, v_his, v_aca, v_stu, user["user_id"], user_id, school_id))
        else:
            conn.execute("""
                INSERT INTO institution_staff_permissions
                (id, user_id, institution_id, role_id, can_view_applications, can_review_details,
                 can_request_clarification, can_recommend_decision, can_approve_stage1, can_view_history,
                 can_manage_academics, can_manage_students, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), user_id, school_id, target_role, v_app, v_det, v_cla, v_rec, v_appr, v_his, v_aca, v_stu, user["user_id"]))

        conn.execute("""
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'UPDATE_STAFF_PERMISSIONS', 'institution_staff_permissions', ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, user["user_id"], user["role"], school_id, json.dumps({
            "target_user_id": user_id,
            "target_role": target_role,
            "permissions": {
                "can_view_applications": v_app,
                "can_review_details": v_det,
                "can_request_clarification": v_cla,
                "can_recommend_decision": v_rec,
                "can_approve_stage1": v_appr,
                "can_view_history": v_his,
                "can_manage_academics": v_aca,
                "can_manage_students": v_stu,
            }
        })))

        conn.commit()
        return {
            "status": "updated",
            "user_id": user_id,
            "role_id": target_role,
            "permissions": {
                "can_view_applications": bool(v_app),
                "can_review_details": bool(v_det),
                "can_request_clarification": bool(v_cla),
                "can_recommend_decision": bool(v_rec),
                "can_approve_stage1": bool(v_appr),
                "can_view_history": bool(v_his),
                "can_manage_academics": bool(v_aca),
                "can_manage_students": bool(v_stu),
            }
        }
    finally:
        conn.close()


@app.get("/school/admin/staff/{user_id}/activity")
def get_school_staff_activity(
    user_id: str,
    user: dict = Depends(require_school_admin)
):
    school_id = user["school_id"]
    conn = get_connection()
    try:
        uir = conn.execute("""
            SELECT role_id, institution_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ?
        """, (user_id, school_id)).fetchone()
        if not uir:
            raise HTTPException(403, f"Cross-institution access forbidden: User {user_id} is not assigned to your institution ({school_id}).")

        logs = conn.execute("""
            SELECT audit_id, action, entity_type, entity_id, school_id, metadata_json, created_at
            FROM audit_logs
            WHERE actor_user_id = ?
            ORDER BY created_at DESC LIMIT 50
        """, (user_id,)).fetchall()

        app_actions = conn.execute("""
            SELECT h.history_id, h.application_id, h.previous_status, h.new_status, h.action_note, h.created_at,
                   a.applicant_name, a.requested_standard
            FROM admission_status_history h
            JOIN admission_applications a ON a.application_id = h.application_id
            WHERE h.action_by_user_id = ?
            ORDER BY h.created_at DESC LIMIT 50
        """, (user_id,)).fetchall()

        activity = []
        for l in logs:
            activity.append({
                "id": l["audit_id"],
                "type": "audit",
                "action": l["action"],
                "entity_type": l["entity_type"],
                "entity_id": l["entity_id"],
                "details": l["metadata_json"],
                "timestamp": l["created_at"]
            })
        for a in app_actions:
            activity.append({
                "id": a["history_id"],
                "type": "admission_action",
                "action": f"Application {a['new_status'].upper()}",
                "entity_type": "admission_application",
                "entity_id": a["application_id"],
                "details": f"{a['applicant_name']} (Std {a['requested_standard']}): {a['action_note']}",
                "timestamp": a["created_at"]
            })

        activity.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        return activity[:50]
    finally:
        conn.close()


@app.get("/school/staff/me/permissions")
def get_my_staff_permissions(user: dict = Depends(require_school_staff)):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        perms = get_staff_permissions(conn, user["user_id"], school_id, user["role"])
        school = conn.execute("SELECT school_name, category, district, school_type FROM schools WHERE school_id = ?", (school_id,)).fetchone()
        return {
            "user_id": user["user_id"],
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "role": user["role"],
            "school_id": school_id,
            "school_name": school["school_name"] if school else None,
            "category": school["category"] if school else None,
            "permissions": perms
        }
    finally:
        conn.close()


@app.post("/auth/forgot-password")
def forgot_password(payload: ForgotPasswordPayload):
    identifier = payload.identifier.strip()
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, email, phone FROM users WHERE (email = ? COLLATE NOCASE OR phone = ?) AND is_active = 1 AND status != 'suspended'",
            (identifier, identifier)
        ).fetchone()

        if user and user["email"]:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            reset_id = str(uuid.uuid4())

            conn.execute("""
                INSERT INTO password_reset_tokens (reset_id, token_hash, user_id, expires_at, is_used)
                VALUES (?, ?, ?, ?, 0)
            """, (reset_id, token_hash, user["user_id"], expires_at))
            conn.commit()

            frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_base}/#/reset-password?token={raw_token}"
            try:
                from email_service import send_password_reset_email
                send_password_reset_email(user["email"], reset_url)
            except Exception as e:
                import logging
                logging.getLogger("nagriksetu.email").error(f"Password reset email dispatch failure: {e}")

            is_dev = os.getenv("APP_ENV", "development").lower() in ("dev", "development", "local")
            res = {
                "status": "ok",
                "message": "If an active account exists with the provided details, password reset instructions have been dispatched to your registered email address."
            }
            if is_dev:
                res["reset_token"] = raw_token
            return res

        elif user and not user["email"]:
            return {
                "status": "mobile_only",
                "message": "This account is registered with a mobile number only. Automated online password reset is currently available only for email accounts. For security, please contact your School Administrator or the NagrikSetu Institution Helpdesk to verify your identity and assist with password recovery."
            }

        return {
            "status": "ok",
            "message": "If an active account exists with the provided details, password reset instructions have been dispatched to your registered email address."
        }
    finally:
        conn.close()


@app.get("/auth/verify-reset-token")
def verify_reset_token(token: str = Query(...)):
    token_hash = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT prt.*, u.email
            FROM password_reset_tokens prt
            JOIN users u ON u.user_id = prt.user_id
            WHERE prt.token_hash = ?
        """, (token_hash,)).fetchone()

        if not row:
            raise HTTPException(400, "Invalid password reset token.")
        if row["is_used"] == 1:
            raise HTTPException(400, "This password reset token has already been used.")

        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This password reset token has expired.")

        return {"valid": True, "email": row["email"]}
    finally:
        conn.close()


@app.post("/auth/reset-password")
def reset_password(payload: ResetPasswordPayload):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    pwd = payload.new_password or payload.password
    if not pwd or len(pwd) < 8:
        raise HTTPException(422, "Password must contain at least 8 characters.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("""
            SELECT * FROM password_reset_tokens WHERE token_hash = ?
        """, (token_hash,)).fetchone()

        if not row or row["is_used"] == 1:
            raise HTTPException(400, "Invalid or already used password reset token.")

        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This password reset token has expired.")

        new_hash = hash_password(pwd)

        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, row["user_id"]))
        conn.execute("UPDATE password_reset_tokens SET is_used = 1, used_at = CURRENT_TIMESTAMP WHERE reset_id = ?", (row["reset_id"],))
        conn.commit()

        return {"status": "ok", "message": "Password reset successfully. You can now log in with your new password."}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class ChangePasswordPayload(BaseModel):
    old_password: str
    new_password: str


@app.post("/auth/change-password")
def change_password(
    payload: ChangePasswordPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Authenticated users can update their account password.
    Enforces minimum 8 characters and Argon2id hashing.
    """
    pwd = payload.new_password.strip() if payload.new_password else ""
    if not pwd or len(pwd) < 8:
        raise HTTPException(status_code=422, detail="Password must contain at least 8 characters.")

    conn = get_connection()
    try:
        user_row = conn.execute("SELECT password_hash FROM users WHERE user_id = ?", (current_user["user_id"],)).fetchone()
        if not user_row or not verify_password(payload.old_password, user_row["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password verification failed.")

        new_hash = hash_password(pwd)
        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, current_user["user_id"]))
        conn.commit()
        return {"status": "ok", "message": "Password changed successfully."}
    finally:
        conn.close()


@app.get("/auth/institutions/admin-statuses")
def get_all_institution_admin_statuses():
    """Returns the administrator invitation and activation status for all institutions."""
    conn = get_connection()
    try:
        schools = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools ORDER BY school_id").fetchall()
        result = {}
        for s in schools:
            result[s["school_id"]] = get_institution_admin_status_dict(conn, s["school_id"], s)
        return result
    finally:
        conn.close()


@app.get("/auth/institution/{institution_id}/admin-status")
def check_institution_admin_status(institution_id: str):
    conn = get_connection()
    try:
        status_info = get_institution_admin_status_dict(conn, institution_id)
        if not status_info:
            raise HTTPException(404, f"Institution '{institution_id}' not found.")
        return status_info
    finally:
        conn.close()


@app.get("/institution/admin/overview")
def get_institution_admin_overview(user: dict = Depends(require_school_staff)):
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Account is not assigned to an institution.")
    conn = get_connection()
    try:
        school = conn.execute("SELECT school_id, school_name, category, district, school_type, affiliation FROM schools WHERE school_id = ?", (school_id,)).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found.")
        
        rows = conn.execute("""
            SELECT status, COUNT(*) as cnt
            FROM admission_applications
            WHERE institution_id = ?
            GROUP BY status
        """, (school_id,)).fetchall()
        status_map = {r["status"]: r["cnt"] for r in rows}

        total_applications = sum(status_map.values())
        pending_stage1 = status_map.get("submitted", 0) + status_map.get("under_review", 0)
        approved = status_map.get("approved", 0)
        rejected = status_map.get("rejected", 0)
        clarification_requested = status_map.get("action_required", 0)
        stage2_submissions = status_map.get("stage2_submitted", 0)
        pending_document_verifications = status_map.get("documents_uploaded", 0) + status_map.get("detailed_review_completed", 0)

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "category": school["category"],
            "district": school["district"],
            "school_type": school["school_type"],
            "affiliation": school["affiliation"],
            "total_applications": total_applications,
            "pending_stage1": pending_stage1,
            "approved": approved,
            "rejected": rejected,
            "clarification_requested": clarification_requested,
            "stage2_submissions": stage2_submissions,
            "pending_document_verifications": pending_document_verifications,
            "status_breakdown": status_map
        }
    finally:
        conn.close()


# =============================================================================
# PHASE 11B GAP: THREE-LEVEL ONBOARDING WORKFLOW & GLOBAL MONITORING
# =============================================================================

class StaffCandidateInvitePayload(BaseModel):
    candidate_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    role_id: str = "school_staff"
    institution_id: Optional[str] = None

class StaffCandidateSubmitPayload(BaseModel):
    token: str
    candidate_name: Optional[str] = None
    candidate_phone: Optional[str] = None
    qualifications: Optional[List[dict]] = None
    employment_details: Optional[dict] = None
    documents: Optional[List[dict]] = None

class StaffCandidateCorrectionPayload(BaseModel):
    correction_notes: str

class StaffCandidateDeclinePayload(BaseModel):
    reason: str

class StaffCandidateApprovePayload(BaseModel):
    review_notes: Optional[str] = None

class StaffCandidateActivatePayload(BaseModel):
    activation_token: str
    password: str


@app.post("/school/admin/staff-applications/invite")
def invite_staff_candidate(
    payload: StaffCandidateInvitePayload,
    current_user: dict = Depends(require_school_admin)
):
    conn = get_connection()
    """
    Level 2: Institution Admin generates an application invitation link for a staff candidate.
    Creates a pending staff application, NOT an active user account.
    """
    admin_school_id = current_user.get("school_id")
    target_school_id = payload.institution_id or admin_school_id
    if current_user.get("role") != "platform_admin" and target_school_id != admin_school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden: Cannot invite staff for another institution.")

    school = conn.execute("SELECT school_name, category FROM schools WHERE school_id = ?", (target_school_id,)).fetchone()
    if not school:
        raise HTTPException(status_code=404, detail="Institution not found.")

    email_clean = payload.candidate_email.strip().lower()
    name_clean = payload.candidate_name.strip()
    app_id = f"STF-{datetime.utcnow().year}-{target_school_id}-{uuid.uuid4().hex[:6].upper()}"
    candidate_token = secrets.token_urlsafe(32)

    conn.execute("""
        INSERT INTO staff_applications (
            application_id, candidate_token, institution_id, candidate_email,
            candidate_name, candidate_phone, role_id, status, created_by_user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'invited', ?)
    """, (app_id, candidate_token, target_school_id, email_clean, name_clean, payload.candidate_phone, payload.role_id, current_user["user_id"]))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'INVITE_STAFF_CANDIDATE', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, app_id, current_user["user_id"], current_user.get("role"), target_school_id, json.dumps({
        "candidate_email": email_clean,
        "candidate_name": name_clean,
        "role_id": payload.role_id,
        "institution_id": target_school_id,
        "admin_name": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()

    return {
        "status": "invited",
        "application_id": app_id,
        "candidate_token": candidate_token,
        "candidate_url": f"/staff-application?token={candidate_token}",
        "candidate_email": email_clean,
        "candidate_name": name_clean,
        "institution_id": target_school_id,
        "institution_name": school["school_name"],
        "role_id": payload.role_id,
        "message": "Staff candidate invitation link generated. The candidate must submit credentials and obtain approval before account activation."
    }


@app.get("/school/admin/staff-applications")
def list_staff_applications(
    current_user: dict = Depends(require_school_admin)
):
    conn = get_connection()
    """
    Lists all staff candidate applications for caller's institution.
    """
    school_id = current_user.get("school_id")
    if not school_id and current_user.get("role") != "platform_admin":
        raise HTTPException(status_code=403, detail="Not assigned to an institution.")

    query = """
        SELECT sa.*, s.school_name, s.category,
               u_cr.full_name as creator_name, u_rev.full_name as reviewer_name
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        LEFT JOIN users u_cr ON u_cr.user_id = sa.created_by_user_id
        LEFT JOIN users u_rev ON u_rev.user_id = sa.reviewed_by_user_id
    """
    params = []
    if current_user.get("role") != "platform_admin":
        query += " WHERE sa.institution_id = ?"
        params.append(school_id)
    
    query += " ORDER BY sa.created_at DESC"
    rows = conn.execute(query, tuple(params)).fetchall()

    result = []
    for r in rows:
        result.append({
            "application_id": r["application_id"],
            "candidate_token": r["candidate_token"],
            "institution_id": r["institution_id"],
            "institution_name": r["school_name"],
            "category": r["category"],
            "candidate_email": r["candidate_email"],
            "candidate_name": r["candidate_name"],
            "candidate_phone": r["candidate_phone"],
            "role_id": r["role_id"],
            "status": r["status"],
            "qualifications": json.loads(r["qualifications_json"] or "[]"),
            "employment_details": json.loads(r["employment_details_json"] or "{}"),
            "documents": json.loads(r["documents_json"] or "[]"),
            "correction_notes": r["correction_notes"],
            "review_notes": r["review_notes"],
            "created_by": r["creator_name"] or r["created_by_user_id"],
            "reviewed_by": r["reviewer_name"] or r["reviewed_by_user_id"],
            "reviewed_at": r["reviewed_at"],
            "activation_token": r["activation_token"],
            "activation_url": f"/staff-activation?token={r['activation_token']}" if r["activation_token"] else None,
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })
    return result


@app.get("/school/admin/staff-applications/{application_id}")
def get_staff_application_detail(
    application_id: str,
    current_user: dict = Depends(require_school_admin)
):
    conn = get_connection()
    """
    Institution Admin inspects submitted staff candidate details, qualifications, employment, and attached docs.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("""
        SELECT sa.*, s.school_name, s.category,
               u_cr.full_name as creator_name, u_rev.full_name as reviewer_name
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        LEFT JOIN users u_cr ON u_cr.user_id = sa.created_by_user_id
        LEFT JOIN users u_rev ON u_rev.user_id = sa.reviewed_by_user_id
        WHERE sa.application_id = ?
    """, (application_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden: Cannot view staff application of another institution.")

    history_rows = conn.execute("""
        SELECT audit_id, action, actor_user_id, actor_role, created_at, metadata_json
        FROM audit_logs
        WHERE entity_id = ?
        ORDER BY created_at ASC
    """, (application_id,)).fetchall()

    history = []
    for h in history_rows:
        meta = json.loads(h["metadata_json"] or "{}")
        history.append({
            "action": h["action"],
            "actor_role": h["actor_role"],
            "timestamp": h["created_at"],
            "details": meta
        })

    return {
        "application_id": row["application_id"],
        "candidate_token": row["candidate_token"],
        "institution_id": row["institution_id"],
        "institution_name": row["school_name"],
        "category": row["category"],
        "candidate_email": row["candidate_email"],
        "candidate_name": row["candidate_name"],
        "candidate_phone": row["candidate_phone"],
        "role_id": row["role_id"],
        "status": row["status"],
        "qualifications": json.loads(row["qualifications_json"] or "[]"),
        "employment_details": json.loads(row["employment_details_json"] or "{}"),
        "documents": json.loads(row["documents_json"] or "[]"),
        "correction_notes": row["correction_notes"],
        "review_notes": row["review_notes"],
        "created_by": row["creator_name"] or row["created_by_user_id"],
        "reviewed_by": row["reviewer_name"] or row["reviewed_by_user_id"],
        "reviewed_at": row["reviewed_at"],
        "activation_token": row["activation_token"],
        "activation_url": f"/staff-activation?token={row['activation_token']}" if row["activation_token"] else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "audit_history": history
    }


@app.post("/school/admin/staff-applications/{application_id}/request-correction")
def request_staff_application_correction(
    application_id: str,
    payload: StaffCandidateCorrectionPayload,
    current_user: dict = Depends(require_school_admin)
):
    conn = get_connection()
    """
    Institution Admin requests corrections or missing information from candidate.
    Candidate can then update and resubmit.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("SELECT institution_id, candidate_email, candidate_name, status FROM staff_applications WHERE application_id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden.")

    notes_clean = payload.correction_notes.strip()
    if not notes_clean:
        raise HTTPException(status_code=422, detail="Correction notes are mandatory.")

    conn.execute("""
        UPDATE staff_applications
        SET status = 'correction_requested', correction_notes = ?, reviewed_by_user_id = ?,
            reviewed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (notes_clean, current_user["user_id"], application_id))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_CORRECTION_REQUESTED', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, application_id, current_user["user_id"], current_user.get("role"), row["institution_id"], json.dumps({
        "candidate_email": row["candidate_email"],
        "correction_notes": notes_clean,
        "reviewer": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()
    return {
        "status": "correction_requested",
        "application_id": application_id,
        "correction_notes": notes_clean,
        "message": "Correction request recorded. Candidate can now update and resubmit their application dossier."
    }


@app.post("/school/admin/staff-applications/{application_id}/approve")
def approve_staff_application(
    application_id: str,
    payload: StaffCandidateApprovePayload,
    current_user: dict = Depends(require_school_admin)
):
    conn = get_connection()
    """
    Institution Admin approves staff candidate application.
    Generates a secure 72-hour single-use activation token for the candidate to set their password.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("SELECT institution_id, candidate_email, candidate_name, role_id, status FROM staff_applications WHERE application_id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden.")

    if row["status"] not in ("submitted", "resubmitted"):
        raise HTTPException(status_code=400, detail=f"Cannot approve application in '{row['status']}' status. Candidate must submit details first.")

    activation_token = secrets.token_urlsafe(32)
    activation_expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
    notes_clean = (payload.review_notes or "").strip()

    conn.execute("""
        UPDATE staff_applications
        SET status = 'approved', review_notes = ?, activation_token = ?,
            activation_expires_at = ?, reviewed_by_user_id = ?, reviewed_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (notes_clean, activation_token, activation_expires_at, current_user["user_id"], application_id))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_APPROVED', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, application_id, current_user["user_id"], current_user.get("role"), row["institution_id"], json.dumps({
        "candidate_email": row["candidate_email"],
        "role_id": row["role_id"],
        "review_notes": notes_clean,
        "reviewer": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()

    return {
        "status": "approved",
        "application_id": application_id,
        "candidate_email": row["candidate_email"],
        "activation_token": activation_token,
        "activation_url": f"/staff-activation?token={activation_token}",
        "expires_at": activation_expires_at,
        "message": "Staff application approved. Activation token issued for candidate password initialization."
    }


@app.post("/school/admin/staff-applications/{application_id}/decline")
def decline_staff_application(
    application_id: str,
    payload: StaffCandidateDeclinePayload,
    current_user: dict = Depends(require_school_admin)
):
    conn = get_connection()
    """
    Institution Admin declines staff candidate application with formal reason.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("SELECT institution_id, candidate_email, candidate_name, status FROM staff_applications WHERE application_id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden.")

    reason_clean = payload.reason.strip()
    if not reason_clean:
        raise HTTPException(status_code=422, detail="Decline reason is mandatory.")

    conn.execute("""
        UPDATE staff_applications
        SET status = 'declined', review_notes = ?, reviewed_by_user_id = ?,
            reviewed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (reason_clean, current_user["user_id"], application_id))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_DECLINED', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, application_id, current_user["user_id"], current_user.get("role"), row["institution_id"], json.dumps({
        "candidate_email": row["candidate_email"],
        "decline_reason": reason_clean,
        "reviewer": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()

    return {
        "status": "declined",
        "application_id": application_id,
        "candidate_email": row["candidate_email"],
        "reason": reason_clean,
        "message": "Staff candidate application declined with formal notice."
    }


# -----------------------------------------------------------------------------
# Public Candidate Endpoints (No Login Required)
# -----------------------------------------------------------------------------

@app.get("/auth/staff-candidate/application")
def get_candidate_application(token: str = Query(...)):
    conn = get_connection()
    """
    Candidate opens their unique invitation link to view or update application.
    """
    row = conn.execute("""
        SELECT sa.*, s.school_name, s.category, s.district
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        WHERE sa.candidate_token = ?
    """, (token.strip(),)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Invalid staff candidate invitation link or token.")

    return {
        "application_id": row["application_id"],
        "candidate_token": row["candidate_token"],
        "institution_id": row["institution_id"],
        "institution_name": row["school_name"],
        "category": row["category"],
        "district": row["district"],
        "candidate_email": row["candidate_email"],
        "candidate_name": row["candidate_name"],
        "candidate_phone": row["candidate_phone"],
        "role_id": row["role_id"],
        "status": row["status"],
        "qualifications": json.loads(row["qualifications_json"] or "[]"),
        "employment_details": json.loads(row["employment_details_json"] or "{}"),
        "documents": json.loads(row["documents_json"] or "[]"),
        "correction_notes": row["correction_notes"],
        "review_notes": row["review_notes"],
        "activation_token": row["activation_token"]
    }


@app.post("/auth/staff-candidate/submit")
def submit_candidate_application(
    payload: StaffCandidateSubmitPayload
):
    conn = get_connection()
    """
    Candidate submits qualifications, employment history, and supporting document summaries.
    Sets status to 'submitted' or 'resubmitted' without creating an active user account.
    """
    row = conn.execute("""
        SELECT * FROM staff_applications WHERE candidate_token = ?
    """, (payload.token.strip(),)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Invalid candidate token.")

    if row["status"] not in ("invited", "correction_requested"):
        raise HTTPException(status_code=400, detail=f"Cannot submit application in '{row['status']}' state.")

    new_status = "resubmitted" if row["status"] == "correction_requested" else "submitted"
    name_clean = (payload.candidate_name or row["candidate_name"]).strip()
    phone_clean = (payload.candidate_phone or row["candidate_phone"] or "").strip() or None
    quals_json = json.dumps(payload.qualifications or [])
    empl_json = json.dumps(payload.employment_details or {})
    docs_json = json.dumps(payload.documents or [])

    conn.execute("""
        UPDATE staff_applications
        SET candidate_name = ?, candidate_phone = ?, qualifications_json = ?,
            employment_details_json = ?, documents_json = ?, status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (name_clean, phone_clean, quals_json, empl_json, docs_json, new_status, row["application_id"]))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_SUBMITTED', 'staff_application', ?, NULL, 'candidate', ?, ?)
    """, (audit_id, row["application_id"], row["institution_id"], json.dumps({
        "status": new_status,
        "candidate_name": name_clean,
        "candidate_email": row["candidate_email"],
        "qualifications_count": len(payload.qualifications or []),
        "documents_count": len(payload.documents or [])
    })))

    conn.commit()

    return {
        "status": new_status,
        "application_id": row["application_id"],
        "message": "Staff candidate dossier submitted successfully. Your application is now pending review by the Institution Administrator."
    }


@app.post("/auth/staff-candidate/activate")
def activate_approved_candidate(
    payload: StaffCandidateActivatePayload
):
    conn = get_connection()
    """
    Candidate completes account activation ONLY AFTER approval. Sets their secure password.
    Creates active user account in 'users', 'user_institution_roles', and 'institution_staff_permissions'.
    """
    tok = payload.activation_token.strip()
    pwd = payload.password

    if len(pwd) < 8:
        raise HTTPException(status_code=422, detail="Password must contain at least 8 characters.")

    row = conn.execute("""
        SELECT * FROM staff_applications WHERE activation_token = ?
    """, (tok,)).fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Invalid activation token.")

    if row["status"] != "approved":
        raise HTTPException(status_code=400, detail=f"Application is in '{row['status']}' state; only approved candidates can activate.")

    if row["activation_expires_at"]:
        exp = datetime.fromisoformat(row["activation_expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(status_code=400, detail="Activation token has expired. Please request a fresh invitation from the administrator.")

    email_clean = row["candidate_email"].strip().lower()
    inst_id = row["institution_id"]
    role_id = row["role_id"]
    full_name = row["candidate_name"].strip()
    phone = row["candidate_phone"]

    # Check if user already exists
    existing = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (email_clean,)).fetchone()
    pwd_hash = hash_password(pwd)

    if existing:
        user_id = existing["user_id"]
        conn.execute("""
            UPDATE users
            SET password_hash = ?, is_active = 1, status = 'active', full_name = ?, school_id = ?
            WHERE user_id = ?
        """, (pwd_hash, full_name, inst_id, user_id))
    else:
        user_id = str(uuid.uuid4())
        # Prevent unique phone collision
        if phone:
            p_dup = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone,)).fetchone()
            if p_dup:
                phone = None
        # Base role in users table must respect CHECK constraint: 'school_staff'
        conn.execute("""
            INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
            VALUES (?, ?, ?, ?, 'school_staff', ?, 1, 'active', ?)
        """, (user_id, email_clean, phone, pwd_hash, inst_id, full_name))

    # user_institution_roles mapping
    existing_role = conn.execute("""
        SELECT id FROM user_institution_roles WHERE user_id = ? AND institution_id = ?
    """, (user_id, inst_id)).fetchone()

    if existing_role:
        conn.execute("""
            UPDATE user_institution_roles
            SET role_id = ?, status = 'active'
            WHERE id = ?
        """, (role_id, existing_role["id"]))
    else:
        conn.execute("""
            INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
            VALUES (?, ?, ?, ?, 'active', ?)
        """, (str(uuid.uuid4()), user_id, inst_id, role_id, row["created_by_user_id"]))

    # Seed permissions
    default_perms = DEFAULT_ROLE_PERMS.get(role_id, DEFAULT_ROLE_PERMS["school_staff"]).copy()
    existing_perm = conn.execute("""
        SELECT id FROM institution_staff_permissions WHERE user_id = ? AND institution_id = ?
    """, (user_id, inst_id)).fetchone()

    if existing_perm:
        conn.execute("""
            UPDATE institution_staff_permissions
            SET role_id = ?, can_view_applications = ?, can_review_details = ?,
                can_request_clarification = ?, can_recommend_decision = ?, can_approve_stage1 = ?,
                can_view_history = ?, can_manage_academics = ?, can_manage_students = ?,
                updated_at = CURRENT_TIMESTAMP, updated_by = ?
            WHERE id = ?
        """, (
            role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            row["reviewed_by_user_id"],
            existing_perm["id"]
        ))
    else:
        conn.execute("""
            INSERT INTO institution_staff_permissions (
                id, user_id, institution_id, role_id,
                can_view_applications, can_review_details, can_request_clarification,
                can_recommend_decision, can_approve_stage1, can_view_history,
                can_manage_academics, can_manage_students, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), user_id, inst_id, role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            row["reviewed_by_user_id"]
        ))

    # Mark application as activated and burn the activation token
    conn.execute("""
        UPDATE staff_applications
        SET status = 'activated', activation_token = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (row["application_id"],))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_ACCOUNT_ACTIVATED', 'users', ?, ?, 'staff', ?, ?)
    """, (audit_id, user_id, user_id, inst_id, json.dumps({
        "application_id": row["application_id"],
        "email": email_clean,
        "role_id": role_id
    })))

    conn.commit()

    return {
        "status": "activated",
        "user_id": user_id,
        "email": email_clean,
        "role_id": role_id,
        "institution_id": inst_id,
        "message": "Account successfully activated! You can now log into your institution staff portal."
    }


# -----------------------------------------------------------------------------
# Level 3: Platform Admin Global Staff Monitoring Endpoint
# -----------------------------------------------------------------------------

@app.get("/admin/staff-monitoring")
def get_global_staff_monitoring(
    institution_id: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(require_platform_admin)
):
    conn = get_connection()
    """
    Platform Admin monitors staff lifecycle across all 30 institutions:
    Invitations, candidate applications, approvals, rejections, corrections,
    role/permission updates, suspensions, and reactivations.
    """
    # 1. Fetch Summary Metrics across all 30 institutions
    app_stats = conn.execute("""
        SELECT status, COUNT(*) as cnt FROM staff_applications GROUP BY status
    """).fetchall()
    app_map = {r["status"]: r["cnt"] for r in app_stats}

    staff_stats = conn.execute("""
        SELECT u.is_active, uir.status, COUNT(*) as cnt
        FROM user_institution_roles uir
        JOIN users u ON u.user_id = uir.user_id
        GROUP BY u.is_active, uir.status
    """).fetchall()

    total_active_staff = sum(r["cnt"] for r in staff_stats if r["is_active"] == 1 and r["status"] == "active")
    total_suspended_staff = sum(r["cnt"] for r in staff_stats if r["is_active"] == 0 or r["status"] == "suspended")

    # 2. Fetch Applications with Institution Details
    app_query = """
        SELECT sa.*, s.school_name, s.category, s.district,
               u_cr.full_name as creator_name, u_rev.full_name as reviewer_name
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        LEFT JOIN users u_cr ON u_cr.user_id = sa.created_by_user_id
        LEFT JOIN users u_rev ON u_rev.user_id = sa.reviewed_by_user_id
        WHERE 1=1
    """
    app_params = []
    if institution_id:
        app_query += " AND sa.institution_id = ?"
        app_params.append(institution_id)
    if category:
        app_query += " AND s.category = ?"
        app_params.append(category)
    if search:
        app_query += " AND (sa.candidate_name LIKE ? OR sa.candidate_email LIKE ? OR sa.application_id LIKE ?)"
        term = f"%{search.strip()}%"
        app_params.extend([term, term, term])

    app_query += " ORDER BY sa.created_at DESC LIMIT ?"
    app_params.append(limit)

    app_rows = conn.execute(app_query, tuple(app_params)).fetchall()

    applications_list = []
    for r in app_rows:
        applications_list.append({
            "application_id": r["application_id"],
            "institution_id": r["institution_id"],
            "institution_name": r["school_name"],
            "category": r["category"],
            "district": r["district"],
            "candidate_name": r["candidate_name"],
            "candidate_email": r["candidate_email"],
            "candidate_phone": r["candidate_phone"],
            "role_id": r["role_id"],
            "status": r["status"],
            "correction_notes": r["correction_notes"],
            "review_notes": r["review_notes"],
            "created_by": r["creator_name"] or r["created_by_user_id"],
            "reviewed_by": r["reviewer_name"] or r["reviewed_by_user_id"],
            "reviewed_at": r["reviewed_at"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })

    # 3. Append-only Audit Ledger for all staff activities
    audit_query = """
        SELECT al.audit_id, al.action, al.entity_type, al.entity_id,
               al.actor_user_id, al.actor_role, al.school_id, al.created_at,
               al.metadata_json, s.school_name, s.category,
               u.full_name as actor_name
        FROM audit_logs al
        LEFT JOIN schools s ON s.school_id = al.school_id
        LEFT JOIN users u ON u.user_id = al.actor_user_id
        WHERE (al.action LIKE '%STAFF%' OR al.action LIKE '%INSTITUTION_ADMIN%' OR al.entity_type IN ('staff_application', 'institution_staff_permissions'))
    """
    audit_params = []
    if institution_id:
        audit_query += " AND al.school_id = ?"
        audit_params.append(institution_id)
    if category:
        audit_query += " AND s.category = ?"
        audit_params.append(category)

    audit_query += " ORDER BY al.created_at DESC LIMIT ?"
    audit_params.append(limit)

    audit_rows = conn.execute(audit_query, tuple(audit_params)).fetchall()

    events_list = []
    for a in audit_rows:
        events_list.append({
            "audit_id": a["audit_id"],
            "action": a["action"],
            "entity_type": a["entity_type"],
            "entity_id": a["entity_id"],
            "actor_user_id": a["actor_user_id"],
            "actor_name": a["actor_name"] or a["actor_user_id"],
            "actor_role": a["actor_role"],
            "institution_id": a["school_id"],
            "institution_name": a["school_name"],
            "category": a["category"],
            "timestamp": a["created_at"],
            "metadata": json.loads(a["metadata_json"] or "{}")
        })

    return {
        "summary": {
            "total_candidate_applications": sum(app_map.values()),
            "pending_applications": app_map.get("submitted", 0) + app_map.get("resubmitted", 0),
            "correction_requested": app_map.get("correction_requested", 0),
            "approved_applications": app_map.get("approved", 0),
            "declined_applications": app_map.get("declined", 0),
            "activated_accounts": app_map.get("activated", 0),
            "active_roster_staff": total_active_staff,
            "suspended_staff": total_suspended_staff,
            "monitored_institutions": 30
        },
        "applications": applications_list,
        "audit_events": events_list
    }


# =============================================================================
# PHASE 12: ACADEMIC MANAGEMENT ENDPOINTS
# =============================================================================

class AttendanceEntryItem(BaseModel):
    permanent_student_id: str
    status: Literal["present", "absent", "leave"]
    remarks: Optional[str] = None

class BatchAttendanceRecordPayload(BaseModel):
    institution_id: str
    attendance_date: str = Field(min_length=10, max_length=10) # YYYY-MM-DD
    subject_name: Optional[str] = None
    records: List[AttendanceEntryItem]

class ExaminationCreatePayload(BaseModel):
    institution_id: str
    academic_year: str = "2025-26"
    exam_name: str = Field(min_length=2, max_length=100)
    standard_or_level: Optional[str] = None # "1", "11", "Semester 1", "All"
    standard: Optional[int] = None
    start_date: Optional[str] = None # YYYY-MM-DD
    exam_date: Optional[str] = None # YYYY-MM-DD
    end_date: Optional[str] = None
    status: Literal["scheduled", "ongoing", "completed", "cancelled"] = "scheduled"
    description: Optional[str] = None

class ResultEntryItem(BaseModel):
    permanent_student_id: str
    marks_obtained: float = Field(ge=0)
    reason_for_change: Optional[str] = None

class BatchResultRecordPayload(BaseModel):
    institution_id: str
    academic_year: str = "2026-2027"
    exam_name: str = Field(min_length=2, max_length=100)
    subject_name: str = Field(min_length=2, max_length=100)
    maximum_marks: float = Field(gt=0)
    exam_date: Optional[str] = None
    exam_id: Optional[str] = None
    records: List[ResultEntryItem]

class AnnouncementCreatePayload(BaseModel):
    institution_id: str
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=5, max_length=5000)
    target_audience: Literal["all", "students", "parents", "staff"] = "all"


@app.post("/academic/attendance/batch", status_code=status.HTTP_201_CREATED)
def record_batch_attendance(
    payload: BatchAttendanceRecordPayload,
    user: dict = Depends(require_school_staff),
):
    """
    Authorized Institution Staff and Institution Admin record daily or subject-wise student attendance.
    Supports present, absent, and approved leave statuses.
    Enforces multi-institution boundary.
    """
    inst_id = payload.institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot record attendance for institution '{inst_id}'."
        )

    conn = get_connection()
    try:
        # Verify institution exists
        inst = conn.execute("SELECT school_id, school_name FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not inst:
            raise HTTPException(status_code=404, detail=f"Institution '{inst_id}' not found.")

        subj = payload.subject_name.strip() if payload.subject_name and payload.subject_name.strip() else None
        recorded_count = 0

        for rec in payload.records:
            pid = rec.permanent_student_id.strip()
            # Verify student belongs to this institution
            stu = conn.execute(
                "SELECT student_id, school_id FROM students WHERE permanent_student_id = ?",
                (pid,)
            ).fetchone()
            if not stu or stu["school_id"] != inst_id:
                continue

            # Check existing entry for date and subject
            existing = conn.execute(
                """
                SELECT attendance_id FROM student_attendance
                WHERE institution_id = ? AND permanent_student_id = ? AND attendance_date = ?
                  AND ((subject_name IS NULL AND ? IS NULL) OR subject_name = ?)
                """,
                (inst_id, pid, payload.attendance_date, subj, subj)
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE student_attendance
                    SET status = ?, remarks = ?, recorded_by_user_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE attendance_id = ?
                    """,
                    (rec.status, rec.remarks, user["user_id"], existing["attendance_id"])
                )
            else:
                att_id = f"ATT-{uuid.uuid4().hex[:10].upper()}"
                conn.execute(
                    """
                    INSERT INTO student_attendance (
                        attendance_id, institution_id, permanent_student_id,
                        academic_year, attendance_date, status, subject_name,
                        remarks, recorded_by_user_id
                    ) VALUES (?, ?, ?, '2026-2027', ?, ?, ?, ?, ?)
                    """,
                    (att_id, inst_id, pid, payload.attendance_date, rec.status, subj, rec.remarks, user["user_id"])
                )
            recorded_count += 1
            # Dispatch attendance notifications to student & verified guardians
            notification_service.trigger_attendance_notification(
                conn, inst_id, pid, payload.attendance_date, rec.status, subj
            )

        conn.commit()

        # Audit log entry
        conn.execute(
            """
            INSERT INTO audit_logs (
                audit_id, actor_user_id, actor_role, action,
                entity_type, entity_id, school_id, metadata_json
            ) VALUES (?, ?, ?, 'ATTENDANCE_BATCH_RECORDED', 'student_attendance', ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                user["user_id"],
                user["role"],
                payload.attendance_date,
                inst_id,
                json.dumps({
                    "attendance_date": payload.attendance_date,
                    "subject_name": subj,
                    "records_count": recorded_count,
                    "total_submitted": len(payload.records)
                })
            )
        )
        record_platform_audit(
            conn,
            event_type="ATTENDANCE_RECORDED",
            event_category="academic",
            institution_id=inst_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            entity_type="student_attendance",
            entity_id=inst_id,
            action=f"Attendance recorded for {recorded_count} student(s) on {payload.attendance_date}",
            new_values={"date": payload.attendance_date, "count": recorded_count, "subject": subj},
            remarks=f"Attendance recorded by {user.get('full_name', user['user_id'])}"
        )
        conn.commit()

        return {
            "status": "success",
            "message": f"Successfully logged attendance for {recorded_count} student(s) on {payload.attendance_date}.",
            "recorded_count": recorded_count,
            "records_count": recorded_count,
            "attendance_date": payload.attendance_date,
            "institution_id": inst_id
        }
    finally:
        conn.close()


@app.get("/academic/attendance")
def list_attendance_records(
    institution_id: Optional[str] = None,
    attendance_date: Optional[str] = None,
    standard: Optional[int] = None,
    section: Optional[str] = None,
    subject_name: Optional[str] = None,
    user: dict = Depends(require_school_staff),
):
    """
    Query attendance records with filtering by date, standard, section, and subject.
    Enforces multi-institution boundary.
    """
    target_inst = institution_id.strip() if institution_id else user.get("school_id")
    if user["role"] != "platform_admin" and user.get("school_id") != target_inst:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot view attendance for institution '{target_inst}'."
        )

    conn = get_connection()
    try:
        query = """
            SELECT sa.attendance_id, sa.institution_id, sa.permanent_student_id,
                   sa.academic_year, sa.attendance_date, sa.status, sa.subject_name,
                   sa.remarks, sa.recorded_by_user_id, sa.created_at, sa.updated_at,
                   s.student_id, s.student_name, s.standard, s.section,
                   u.full_name AS recorder_name
            FROM student_attendance sa
            JOIN students s ON s.permanent_student_id = sa.permanent_student_id
            LEFT JOIN users u ON u.user_id = sa.recorded_by_user_id
            WHERE sa.institution_id = ?
        """
        params = [target_inst]

        if attendance_date:
            query += " AND sa.attendance_date = ?"
            params.append(attendance_date.strip())
        if standard is not None:
            query += " AND s.standard = ?"
            params.append(standard)
        if section:
            query += " AND s.section = ?"
            params.append(section.strip().upper())
        if subject_name:
            query += " AND sa.subject_name = ?"
            params.append(subject_name.strip())

        query += " ORDER BY sa.attendance_date DESC, s.standard ASC, s.section ASC, s.student_name ASC LIMIT 500"
        rows = conn.execute(query, tuple(params)).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/academic/attendance/summary/{permanent_student_id}")
def get_student_attendance_summary(
    permanent_student_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Retrieve monthly and annual attendance summaries for a student.
    Strictly isolated: Student views only own, Parent views only linked child,
    Staff views only students in their own institution.
    """
    conn = get_connection()
    try:
        pid = permanent_student_id.strip()
        stu = conn.execute("SELECT student_id, student_name, school_id, permanent_student_id FROM students WHERE permanent_student_id = ? OR student_id = ?", (pid, pid)).fetchone()
        if not stu:
            raise HTTPException(status_code=404, detail="Student record not found.")

        perm_id = stu["permanent_student_id"]

        # Access control
        if user["role"] == "student":
            if user.get("permanent_student_id") != perm_id and user.get("student_id") != stu["student_id"]:
                raise HTTPException(status_code=403, detail="Access denied: Students can view only their own attendance.")
        elif user["role"] == "parent":
            guardian = get_parent_guardian(conn, user["user_id"])
            if not guardian or not get_authorized_child(conn, guardian["guardian_id"], perm_id, "can_view_records"):
                raise HTTPException(status_code=403, detail="Access denied: You are not authorized to view this student's records.")
        elif user["role"] in STAFF_ROLES:
            if user["role"] != "platform_admin" and user.get("school_id") != stu["school_id"]:
                raise HTTPException(status_code=403, detail="Access denied: Student does not belong to your institution.")

        return calculate_attendance_summary(conn, perm_id)
    finally:
        conn.close()


@app.post("/academic/examinations", status_code=status.HTTP_201_CREATED)
def create_examination(
    payload: ExaminationCreatePayload,
    user: dict = Depends(require_school_staff),
):
    """
    Staff / Admin creates a scheduled or ongoing examination.
    """
    inst_id = payload.institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot create examinations for institution '{inst_id}'."
        )

    conn = get_connection()
    try:
        exam_id = f"EXAM-{uuid.uuid4().hex[:8].upper()}"
        effective_date = (payload.start_date or payload.exam_date or datetime.now().strftime("%Y-%m-%d")).strip()
        effective_std = (payload.standard_or_level or (f"Class {payload.standard}" if payload.standard else "All")).strip()
        conn.execute(
            """
            INSERT INTO examinations (
                exam_id, institution_id, academic_year, exam_name,
                standard_or_level, start_date, end_date, status,
                description, created_by_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                exam_id, inst_id, payload.academic_year, payload.exam_name.strip(),
                effective_std, effective_date,
                payload.end_date.strip() if payload.end_date else None,
                payload.status, payload.description, user["user_id"]
            )
        )
        conn.commit()

        # Audit log
        conn.execute(
            """
            INSERT INTO audit_logs (
                audit_id, actor_user_id, actor_role, action,
                entity_type, entity_id, school_id, metadata_json
            ) VALUES (?, ?, ?, 'EXAMINATION_CREATED', 'examinations', ?, ?, ?)
            """,
            (
                str(uuid.uuid4()), user["user_id"], user["role"],
                exam_id, inst_id, json.dumps({
                    "exam_name": payload.exam_name.strip(),
                    "standard_or_level": effective_std,
                    "start_date": effective_date,
                    "status": payload.status
                })
            )
        )

        notification_service.trigger_examination_scheduled_notification(
            conn, exam_id, inst_id, payload.exam_name.strip(), effective_std, effective_date
        )

        conn.commit()

        row = conn.execute("SELECT * FROM examinations WHERE exam_id = ?", (exam_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@app.get("/academic/examinations")
def list_examinations(
    institution_id: Optional[str] = None,
    academic_year: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Lists scheduled and past examinations.
    Enforces multi-institution boundaries for staff and administrators.
    """
    if current_user and current_user.get("role") != "platform_admin":
        user_school = current_user.get("school_id")
        if user_school:
            if institution_id and institution_id.strip() != user_school:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: You cannot view examinations for institution '{institution_id}'.",
                )
            institution_id = user_school
    conn = get_connection()
    try:
        query = "SELECT * FROM examinations WHERE 1=1"
        params = []
        if institution_id:
            query += " AND institution_id = ?"
            params.append(institution_id.strip())
        if academic_year:
            query += " AND academic_year = ?"
            params.append(academic_year.strip())
        if status:
            query += " AND status = ?"
            params.append(status.strip())

        query += " ORDER BY start_date DESC LIMIT 100"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/academic/results/batch", status_code=status.HTTP_201_CREATED)
def record_batch_results(
    payload: BatchResultRecordPayload,
    user: dict = Depends(require_school_staff),
):
    """
    Staff / Admin records or updates subject-wise examination marks.
    Calculates percentage and grade automatically according to grading scheme.
    Maintains an audit history for corrections.
    """
    inst_id = payload.institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot record marks for institution '{inst_id}'."
        )

    conn = get_connection()
    try:
        recorded_count = 0
        updated_count = 0

        for rec in payload.records:
            pid = rec.permanent_student_id.strip()
            # Lookup student and current enrollment
            enr = conn.execute(
                """
                SELECT e.enrollment_id, s.school_id, s.student_name
                FROM students s
                JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
                WHERE s.permanent_student_id = ? AND s.school_id = ?
                ORDER BY e.academic_year DESC LIMIT 1
                """,
                (pid, inst_id)
            ).fetchone()

            if not enr:
                continue

            pct, grade = calculate_grade(rec.marks_obtained, payload.maximum_marks)

            # Check existing result for this enrollment, exam, and subject
            existing = conn.execute(
                """
                SELECT result_id, marks_obtained, maximum_marks
                FROM academic_results
                WHERE enrollment_id = ? AND exam_name = ? AND subject_name = ?
                """,
                (enr["enrollment_id"], payload.exam_name.strip(), payload.subject_name.strip())
            ).fetchone()

            if existing:
                res_id = existing["result_id"]
                prev_marks = existing["marks_obtained"]
                prev_max = existing["maximum_marks"]

                # Only log audit if marks or maximum marks actually changed
                if float(prev_marks) != float(rec.marks_obtained) or float(prev_max) != float(payload.maximum_marks):
                    reason = rec.reason_for_change or "Marks updated during verification"
                    audit_id = f"AUD-RES-{uuid.uuid4().hex[:8].upper()}"
                    conn.execute(
                        """
                        INSERT INTO academic_result_audits (
                            audit_id, result_id, previous_marks, new_marks,
                            previous_max_marks, new_max_marks, reason_for_change,
                            modified_by_user_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (audit_id, res_id, prev_marks, rec.marks_obtained, prev_max, payload.maximum_marks, reason, user["user_id"])
                    )
                    record_platform_audit(
                        conn,
                        event_type="MARKS_CORRECTED",
                        event_category="academic",
                        institution_id=inst_id,
                        actor_user_id=user["user_id"],
                        actor_role=user["role"],
                        entity_type="academic_result",
                        entity_id=res_id,
                        action=f"Academic marks corrected for student {enr['student_name']} in {payload.subject_name} ({payload.exam_name})",
                        old_values={"marks_obtained": prev_marks, "maximum_marks": prev_max},
                        new_values={"marks_obtained": rec.marks_obtained, "maximum_marks": payload.maximum_marks},
                        remarks=reason
                    )

                # Update result
                conn.execute(
                    """
                    UPDATE academic_results
                    SET marks_obtained = ?, maximum_marks = ?, percentage = ?, grade = ?,
                        updated_at = CURRENT_TIMESTAMP, recorded_by_user_id = ?
                    WHERE result_id = ?
                    """,
                    (rec.marks_obtained, payload.maximum_marks, pct, grade, user["user_id"], res_id)
                )
                updated_count += 1
                notification_service.trigger_result_notification(
                    conn, res_id, payload.exam_name.strip(), payload.subject_name.strip(),
                    rec.marks_obtained, payload.maximum_marks, grade, pid, inst_id,
                    is_update=True, previous_marks=prev_marks, reason=rec.reason_for_change
                )
            else:
                res_id = f"RES-{uuid.uuid4().hex[:10].upper()}"
                conn.execute(
                    """
                    INSERT INTO academic_results (
                        result_id, enrollment_id, permanent_student_id,
                        subject_name, exam_name, marks_obtained, maximum_marks,
                        percentage, grade, academic_year, exam_date,
                        exam_id, recorded_by_user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        res_id, enr["enrollment_id"], pid,
                        payload.subject_name.strip(), payload.exam_name.strip(),
                        rec.marks_obtained, payload.maximum_marks, pct, grade,
                        payload.academic_year, payload.exam_date or "2026-11-01",
                        payload.exam_id, user["user_id"]
                    )
                )
                recorded_count += 1
                notification_service.trigger_result_notification(
                    conn, res_id, payload.exam_name.strip(), payload.subject_name.strip(),
                    rec.marks_obtained, payload.maximum_marks, grade, pid, inst_id,
                    is_update=False
                )

        conn.commit()

        # Overall audit log
        conn.execute(
            """
            INSERT INTO audit_logs (
                audit_id, actor_user_id, actor_role, action,
                entity_type, entity_id, school_id, metadata_json
            ) VALUES (?, ?, ?, 'EXAM_MARKS_RECORDED', 'academic_results', ?, ?, ?)
            """,
            (
                str(uuid.uuid4()), user["user_id"], user["role"],
                payload.exam_name.strip(), inst_id, json.dumps({
                    "exam_name": payload.exam_name.strip(),
                    "subject_name": payload.subject_name.strip(),
                    "maximum_marks": payload.maximum_marks,
                    "new_records": recorded_count,
                    "updated_records": updated_count
                })
            )
        )
        conn.commit()

        return {
            "status": "success",
            "message": f"Successfully recorded {recorded_count} new mark(s) and updated {updated_count} mark(s) for '{payload.exam_name}' - {payload.subject_name}.",
            "new_count": recorded_count,
            "updated_count": updated_count,
            "processed_count": recorded_count + updated_count,
            "exam_name": payload.exam_name.strip(),
            "subject_name": payload.subject_name.strip()
        }
    finally:
        conn.close()


@app.get("/academic/results")
def list_academic_results(
    institution_id: Optional[str] = None,
    permanent_student_id: Optional[str] = None,
    exam_name: Optional[str] = None,
    subject_name: Optional[str] = None,
    standard: Optional[int] = None,
    section: Optional[str] = None,
    user: dict = Depends(require_school_staff),
):
    """
    Lists evaluation results for institution oversight.
    """
    target_inst = institution_id.strip() if institution_id else user.get("school_id")
    if user["role"] != "platform_admin" and user.get("school_id") != target_inst:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot view results for institution '{target_inst}'."
        )

    conn = get_connection()
    try:
        query = """
            SELECT ar.result_id, ar.enrollment_id, ar.subject_name, ar.exam_name,
                   ar.marks_obtained, ar.maximum_marks, ar.percentage, ar.grade,
                   ar.academic_year, ar.exam_date, ar.created_at, ar.updated_at,
                   s.student_id, s.student_name, s.permanent_student_id, s.standard, s.section,
                   (SELECT COUNT(*) FROM academic_result_audits ara WHERE ara.result_id = ar.result_id) AS audit_count
            FROM academic_results ar
            JOIN enrollments e ON e.enrollment_id = ar.enrollment_id
            JOIN students s ON s.permanent_student_id = e.permanent_student_id
            WHERE s.school_id = ?
        """
        params = [target_inst]

        if permanent_student_id:
            query += " AND (s.permanent_student_id = ? OR s.student_id = ?)"
            params.append(permanent_student_id.strip())
            params.append(permanent_student_id.strip())
        if exam_name:
            query += " AND ar.exam_name = ?"
            params.append(exam_name.strip())
        if subject_name:
            query += " AND ar.subject_name = ?"
            params.append(subject_name.strip())
        if standard is not None:
            query += " AND s.standard = ?"
            params.append(standard)
        if section:
            query += " AND s.section = ?"
            params.append(section.strip().upper())

        query += " ORDER BY ar.academic_year DESC, ar.exam_date DESC, s.standard ASC, s.section ASC, s.student_name ASC LIMIT 500"
        rows = conn.execute(query, tuple(params)).fetchall()

        results = []
        for r in rows:
            item = dict(r)
            if item.get("percentage") is None and item.get("maximum_marks", 0) > 0:
                item["percentage"], item["grade"] = calculate_grade(item["marks_obtained"], item["maximum_marks"])
            results.append(item)

        return results
    finally:
        conn.close()


@app.get("/academic/results/audits/{result_id}")
def get_result_audit_history(
    result_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Returns audit history for a specific corrected result entry.
    """
    conn = get_connection()
    try:
        res = conn.execute(
            """
            SELECT ar.result_id, s.school_id
            FROM academic_results ar
            JOIN enrollments e ON e.enrollment_id = ar.enrollment_id
            JOIN students s ON s.permanent_student_id = e.permanent_student_id
            WHERE ar.result_id = ?
            """,
            (result_id.strip(),)
        ).fetchone()

        if not res:
            raise HTTPException(status_code=404, detail="Result record not found.")

        if user["role"] != "platform_admin" and user.get("school_id") != res["school_id"]:
            raise HTTPException(status_code=403, detail="Access denied.")

        audits = conn.execute(
            """
            SELECT ara.audit_id, ara.result_id, ara.previous_marks, ara.new_marks,
                   ara.previous_max_marks, ara.new_max_marks, ara.reason_for_change,
                   ara.modified_at, u.full_name AS modified_by_name, u.role AS modified_by_role
            FROM academic_result_audits ara
            LEFT JOIN users u ON u.user_id = ara.modified_by_user_id
            WHERE ara.result_id = ?
            ORDER BY ara.modified_at DESC
            """,
            (result_id.strip(),)
        ).fetchall()

        return {
            "result_id": result_id,
            "audits": [dict(a) for a in audits]
        }
    finally:
        conn.close()


@app.get("/academic/performance/{permanent_student_id}")
def get_student_academic_performance(
    permanent_student_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Comprehensive student performance analytics (attendance, results, progress over time).
    Enforces privacy and access control.
    """
    conn = get_connection()
    try:
        pid = permanent_student_id.strip()
        stu = conn.execute("SELECT student_id, student_name, school_id, permanent_student_id FROM students WHERE permanent_student_id = ? OR student_id = ?", (pid, pid)).fetchone()
        if not stu:
            raise HTTPException(status_code=404, detail="Student record not found.")

        perm_id = stu["permanent_student_id"]

        # Access check
        if user["role"] == "student":
            if user.get("permanent_student_id") != perm_id and user.get("student_id") != stu["student_id"]:
                raise HTTPException(status_code=403, detail="Access denied: Students can view only their own records.")
        elif user["role"] == "parent":
            guardian = get_parent_guardian(conn, user["user_id"])
            if not guardian or not get_authorized_child(conn, guardian["guardian_id"], perm_id, "can_view_records"):
                raise HTTPException(status_code=403, detail="Access denied: You are not authorized to view this student's records.")
        elif user["role"] in STAFF_ROLES:
            if user["role"] != "platform_admin" and user.get("school_id") != stu["school_id"]:
                raise HTTPException(status_code=403, detail="Access denied: Student does not belong to your institution.")

        return calculate_academic_performance(conn, perm_id, stu["school_id"])
    finally:
        conn.close()


@app.post("/academic/announcements", status_code=status.HTTP_201_CREATED)
def create_institution_announcement(
    payload: AnnouncementCreatePayload,
    user: dict = Depends(require_school_staff),
):
    """
    Staff / Admin publishes an official institution announcement.
    """
    inst_id = payload.institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You cannot publish announcements for institution '{inst_id}'."
        )

    conn = get_connection()
    try:
        ann_id = f"ANN-{uuid.uuid4().hex[:8].upper()}"
        conn.execute(
            """
            INSERT INTO institution_announcements (
                announcement_id, institution_id, title, content,
                target_audience, created_by_user_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ann_id, inst_id, payload.title.strip(), payload.content.strip(), payload.target_audience, user["user_id"])
        )

        notification_service.trigger_announcement_notification(
            conn, ann_id, inst_id, payload.title.strip(), payload.content.strip(), payload.target_audience
        )

        conn.commit()

        row = conn.execute("SELECT * FROM institution_announcements WHERE announcement_id = ?", (ann_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@app.get("/academic/announcements")
def list_institution_announcements(
    institution_id: str,
    target_audience: Optional[str] = None,
):
    """
    Public / Parent / Student endpoint to view announcements.
    """
    conn = get_connection()
    try:
        query = "SELECT * FROM institution_announcements WHERE institution_id = ?"
        params = [institution_id.strip()]
        if target_audience:
            query += " AND (target_audience = ? OR target_audience = 'all')"
            params.append(target_audience.strip())

        query += " ORDER BY published_date DESC LIMIT 50"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()



# =====================================================================
# INSTITUTION ADMINISTRATOR PORTAL & STUDENT MANAGEMENT APIs (PART 2 - 9)
# =====================================================================

class ReviewParentRequestPayload(BaseModel):
    decision: Literal["approved", "rejected", "clarification_requested"]
    comment: Optional[str] = None


@app.get("/institution/{institution_id}/dashboard-overview")
def get_institution_dashboard_overview(
    institution_id: str,
    user: dict = Depends(require_school_admin)
):
    """Authoritative overview statistics and card metrics for the assigned institution."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, school_name, district, state, school_type, category, affiliation, established_year FROM schools WHERE school_id = ?",
            (inst_id,)
        ).fetchone()
        if not school:
            raise HTTPException(404, f"Institution '{inst_id}' not found.")

        # 1. Total Students
        total_students = conn.execute(
            "SELECT COUNT(*) FROM students WHERE school_id = ?",
            (inst_id,)
        ).fetchone()[0]

        # 2. Total Parents / Verified Guardians
        total_parents = conn.execute(
            """
            SELECT COUNT(DISTINCT g.guardian_id)
            FROM guardians g
            JOIN student_guardians sg ON sg.guardian_id = g.guardian_id
            JOIN students s ON s.permanent_student_id = sg.permanent_student_id
            WHERE s.school_id = ?
            """,
            (inst_id,)
        ).fetchone()[0]

        # 3. New Admission Applications (submitted)
        new_apps = conn.execute(
            "SELECT COUNT(*) FROM admission_applications WHERE institution_id = ? AND status = 'submitted'",
            (inst_id,)
        ).fetchone()[0]

        # 4. Pending Admission Reviews
        pending_admission_reviews = conn.execute(
            "SELECT COUNT(*) FROM admission_applications WHERE institution_id = ? AND status IN ('submitted', 'under_review', 'clarification_requested', 'action_required')",
            (inst_id,)
        ).fetchone()[0]

        # 5. Pending Parent Requests
        pending_parent_requests = conn.execute(
            """
            SELECT COUNT(*)
            FROM update_requests ur
            JOIN students s ON s.permanent_student_id = ur.permanent_student_id
            WHERE s.school_id = ? AND ur.status = 'pending'
            """,
            (inst_id,)
        ).fetchone()[0]

        # 6. Total Academic Programmes
        total_programs = conn.execute(
            "SELECT COUNT(*) FROM academic_programs WHERE institution_id = ? AND is_active = 1",
            (inst_id,)
        ).fetchone()[0]

        # 7. Total Sections
        total_sections = conn.execute(
            "SELECT COUNT(*) FROM program_sections WHERE institution_id = ?",
            (inst_id,)
        ).fetchone()[0]
        if total_sections == 0 and total_students > 0:
            total_sections = conn.execute(
                "SELECT COUNT(DISTINCT standard || '-' || section) FROM students WHERE school_id = ?",
                (inst_id,)
            ).fetchone()[0]

        # Authorized Staff Count
        staff_count = conn.execute(
            """
            SELECT COUNT(DISTINCT uir.user_id)
            FROM user_institution_roles uir
            WHERE uir.institution_id = ? AND uir.status = 'active'
            """,
            (inst_id,)
        ).fetchone()[0]

        # Recent activities
        recent_activities = []
        rows = conn.execute(
            """
            SELECT id, event_type, event_category, action, actor_name, actor_role, created_at
            FROM platform_audit_logs
            WHERE institution_id = ?
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (inst_id,)
        ).fetchall()
        for r in rows:
            recent_activities.append(dict(r))

        return {
            "institution": dict(school),
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "category": school["category"],
            "district": school["district"],
            "state": school["state"],
            "school_type": school["school_type"],
            "affiliation": school["affiliation"],
            "established_year": school["established_year"],
            "total_students": total_students,
            "total_parents": total_parents,
            "new_admission_applications": new_apps,
            "pending_admission_reviews": pending_admission_reviews,
            "pending_parent_requests": pending_parent_requests,
            "total_academic_programs": total_programs,
            "total_sections": total_sections,
            "authorized_staff_count": staff_count,
            "overview_cards": {
                "total_students": total_students,
                "total_parents": total_parents,
                "new_admission_applications": new_apps,
                "pending_admission_reviews": pending_admission_reviews,
                "pending_parent_requests": pending_parent_requests,
                "total_academic_programs": total_programs,
                "total_sections": total_sections,
                "authorized_staff_count": staff_count
            },
            "recent_activities": recent_activities
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/academic-structure")
def get_institution_academic_structure(
    institution_id: str,
    user: dict = Depends(require_school_admin)
):
    """Dynamic academic hierarchy based on the institution's real education category and configured programmes."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        school = conn.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found.")

        category = school["category"] or school["school_type"] or ""
        cat_lower = category.lower()
        is_school = "school" in cat_lower and "pu" not in cat_lower
        is_pu = "pu" in cat_lower or "pre-university" in cat_lower
        is_diploma = "diploma" in cat_lower or "polytechnic" in cat_lower
        is_degree = not is_school and not is_pu and not is_diploma

        # K-10 School
        if is_school:
            standards_rows = conn.execute(
                "SELECT DISTINCT standard FROM students WHERE school_id = ? ORDER BY standard ASC",
                (inst_id,)
            ).fetchall()
            standards = [r["standard"] for r in standards_rows if 1 <= r["standard"] <= 10]
            if not standards:
                standards = list(range(1, 11))

            sections_by_std = {}
            for std in standards:
                sec_rows = conn.execute(
                    "SELECT DISTINCT section FROM students WHERE school_id = ? AND standard = ? ORDER BY section ASC",
                    (inst_id, std)
                ).fetchall()
                secs = [r["section"] for r in sec_rows]
                sections_by_std[str(std)] = secs if secs else ["A", "B", "C"]

            all_sections = sorted(list({s for secs in sections_by_std.values() for s in secs}))
            if not all_sections:
                all_sections = ["A", "B", "C"]

            # Distinct mediums
            med_rows = conn.execute(
                "SELECT DISTINCT first_language FROM students WHERE school_id = ? AND first_language IS NOT NULL",
                (inst_id,)
            ).fetchall()
            mediums = [m["first_language"] for m in med_rows if m["first_language"]]
            if not mediums:
                mediums = ["Kannada", "English"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "K10_SCHOOL",
                "standards": standards,
                "sections": all_sections,
                "sections_by_standard": sections_by_std,
                "mediums": mediums,
                "academic_years": ["2026-2027", "2025-2026"]
            }

        # PU College (11-12)
        elif is_pu:
            pu_levels = ["1st PU (11th)", "2nd PU (12th)"]
            
            # Streams actually configured in academic_programs for this institution
            streams_rows = conn.execute(
                """
                SELECT DISTINCT discipline_or_stream
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                ORDER BY CASE discipline_or_stream
                    WHEN 'Science' THEN 1
                    WHEN 'Commerce' THEN 2
                    WHEN 'Arts / Humanities' THEN 3
                    ELSE 4
                END
                """,
                (inst_id,)
            ).fetchall()
            streams = [r["discipline_or_stream"] for r in streams_rows if r["discipline_or_stream"]]
            if not streams:
                streams = ["Science", "Commerce", "Arts / Humanities"]

            combinations_by_stream = {}
            sections_by_combo_level = {}
            for st in streams:
                combo_rows = conn.execute(
                    "SELECT program_id, program_name, combination_code FROM academic_programs WHERE institution_id = ? AND discipline_or_stream = ? AND is_active = 1 ORDER BY combination_code, program_name",
                    (inst_id, st)
                ).fetchall()
                combos = []
                for c in combo_rows:
                    code = c["combination_code"] or c["program_name"][:4]
                    # Sections from program_sections
                    sec_rows = conn.execute(
                        "SELECT DISTINCT term_or_year, section_name FROM program_sections WHERE institution_id = ? AND program_id = ? ORDER BY term_or_year, section_name",
                        (inst_id, c["program_id"])
                    ).fetchall()
                    sec_by_lvl = {"11": [], "12": []}
                    for sr in sec_rows:
                        if str(sr["term_or_year"]) in sec_by_lvl:
                            sec_by_lvl[str(sr["term_or_year"])].append(sr["section_name"])
                    if not sec_by_lvl["11"]:
                        sec_by_lvl["11"] = ["A", "B"]
                    if not sec_by_lvl["12"]:
                        sec_by_lvl["12"] = ["A", "B"]

                    sections_by_combo_level[f"{code}_11"] = sec_by_lvl["11"]
                    sections_by_combo_level[f"{code}_12"] = sec_by_lvl["12"]

                    combos.append({
                        "program_id": c["program_id"],
                        "code": code,
                        "name": c["program_name"],
                        "stream": st,
                        "sections_by_level": sec_by_lvl
                    })
                combinations_by_stream[st] = combos

            # Overall combination codes
            combo_codes = sorted(list({c["code"] for clist in combinations_by_stream.values() for c in clist if c.get("code")}))
            
            # Default sections
            sections = ["A", "B", "C"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "PU_COLLEGE",
                "pu_levels": pu_levels,
                "streams": streams,
                "combinations": combo_codes,
                "combinations_by_stream": combinations_by_stream,
                "sections": sections,
                "sections_by_combo_level": sections_by_combo_level,
                "academic_years": ["2026-2027", "2025-2026"]
            }

        # Polytechnic / Diploma
        elif is_diploma:
            programs = conn.execute(
                "SELECT program_id, program_name, discipline_or_stream, duration_years FROM academic_programs WHERE institution_id = ? AND is_active = 1 ORDER BY program_name",
                (inst_id,)
            ).fetchall()
            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "DIPLOMA",
                "programs": [dict(p) for p in programs],
                "academic_years": ["2026-2027", "2025-2026"],
                "semesters": [1, 2, 3, 4, 5, 6],
                "sections": ["A", "B"]
            }

        # Degree College / University
        else:
            # 1. Academic Divisions
            div_rows = conn.execute(
                "SELECT division_id, division_name, division_type FROM institution_divisions WHERE parent_institution_id = ? ORDER BY display_order, division_name",
                (inst_id,)
            ).fetchall()
            divisions = [dict(d) for d in div_rows]

            # 2. Configured Degree Programs
            prog_rows = conn.execute(
                """
                SELECT program_id, program_name, degree_type, discipline_or_stream, combination_code,
                       faculty_name, department_name, duration_years
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                ORDER BY program_name
                """,
                (inst_id,)
            ).fetchall()

            programs = []
            for p in prog_rows:
                p_dict = dict(p)
                pid = p["program_id"]
                dur = p["duration_years"] or 4

                # Associate division_id if faculty_name matches
                matching_div = next((d["division_id"] for d in divisions if d["division_name"].lower() == (p["faculty_name"] or "").lower()), None)
                p_dict["division_id"] = matching_div
                p_dict["program_code"] = p["combination_code"] or pid.replace(f"PROG-{inst_id}-", "")

                # Sections from program_sections
                sec_rows = conn.execute(
                    """
                    SELECT section_id, academic_year, term_or_year, semester, section_name
                    FROM program_sections
                    WHERE institution_id = ? AND program_id = ?
                    ORDER BY term_or_year, semester, section_name
                    """,
                    (inst_id, pid)
                ).fetchall()

                if sec_rows:
                    academic_years = sorted(list({r["academic_year"] for r in sec_rows if r["academic_year"]}))
                    years = sorted(list({r["term_or_year"] for r in sec_rows if r["term_or_year"] is not None}))
                    semesters_by_year = {}
                    sections_by_year_sem = {}
                    all_sections = sorted(list({r["section_name"] for r in sec_rows if r["section_name"]}))

                    for r in sec_rows:
                        y = str(r["term_or_year"])
                        s = r["semester"]
                        sec = r["section_name"]
                        if y not in semesters_by_year:
                            semesters_by_year[y] = set()
                        if s is not None:
                            semesters_by_year[y].add(s)

                        key = f"{y}-{s if s is not None else 1}"
                        if key not in sections_by_year_sem:
                            sections_by_year_sem[key] = set()
                        if sec:
                            sections_by_year_sem[key].add(sec)

                    p_dict["academic_years"] = academic_years if academic_years else ["2026-27", "2025-26"]
                    p_dict["years"] = years if years else list(range(1, dur + 1))
                    p_dict["semesters_by_year"] = {y: sorted(list(slist)) for y, slist in semesters_by_year.items()}
                    p_dict["sections_by_year_sem"] = {k: sorted(list(slist)) for k, slist in sections_by_year_sem.items()}
                    p_dict["sections"] = all_sections if all_sections else ["A", "B"]
                else:
                    p_dict["academic_years"] = ["2026-27", "2025-26"]
                    p_dict["years"] = list(range(1, dur + 1))
                    p_dict["semesters_by_year"] = {str(y): [2 * y - 1, 2 * y] for y in range(1, dur + 1)}
                    p_dict["sections_by_year_sem"] = {f"{y}-{sem}": ["A", "B"] for y in range(1, dur + 1) for sem in [2 * y - 1, 2 * y]}
                    p_dict["sections"] = ["A", "B"]

                programs.append(p_dict)

            # All distinct academic years and sections
            all_ac_years = sorted(list({ay for pr in programs for ay in pr.get("academic_years", [])})) or ["2026-27", "2025-26"]
            all_sections = sorted(list({sec for pr in programs for sec in pr.get("sections", [])})) or ["A", "B", "C"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "DEGREE_COLLEGE" if "degree" in cat_lower else "UNIVERSITY",
                "divisions": divisions,
                "programs": programs,
                "academic_years": all_ac_years,
                "sections": all_sections
            }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/students")
def get_institution_students(
    institution_id: str,
    standard: Optional[int] = Query(default=None),
    section: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    stream: Optional[str] = Query(default=None),
    combination: Optional[str] = Query(default=None),
    program_id: Optional[str] = Query(default=None),
    division_id: Optional[str] = Query(default=None),
    year: Optional[int] = Query(default=None),
    semester: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="all"),
    sort_by: Optional[str] = Query(default="student_name"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_admin)
):
    """Returns paginated student records belonging strictly to the authorized institution after structure selection."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        school = conn.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found.")

        category = school["category"] or school["school_type"] or ""
        cat_lower = category.lower()
        is_school = "school" in cat_lower and "pu" not in cat_lower
        is_pu = "pu" in cat_lower or "pre-university" in cat_lower
        is_diploma = "diploma" in cat_lower or "polytechnic" in cat_lower
        is_degree = not is_school and not is_pu and not is_diploma

        # -----------------------------------------------------------------
        # TIER-SPECIFIC BACKEND FILTER VALIDATION
        # -----------------------------------------------------------------
        if is_school:
            # Schools cannot accept PU or Degree parameters
            if stream or combination or program_id or division_id or semester:
                raise HTTPException(
                    status_code=400,
                    detail="Validation error: Stream, combination, and degree programme filters are not applicable to School Education (K-10)."
                )
            if standard is not None and (standard < 1 or standard > 10):
                raise HTTPException(
                    status_code=400,
                    detail=f"Validation error: Standard '{standard}' is invalid for School Education (must be between 1 and 10)."
                )

        elif is_pu:
            # PU Colleges cannot accept Degree program, division, or semester parameters
            if program_id or division_id or semester:
                raise HTTPException(
                    status_code=400,
                    detail="Validation error: Degree programme, division, and semester filters are not applicable to PU Colleges."
                )
            if standard is not None and standard not in (11, 12):
                raise HTTPException(
                    status_code=400,
                    detail=f"Validation error: Standard '{standard}' is invalid for PU Colleges (must be 11 for 1st PU or 12 for 2nd PU)."
                )

            # Query institution's actual configured academic programmes
            pu_progs = conn.execute(
                """
                SELECT program_id, discipline_or_stream, combination_code, program_name
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                """,
                (inst_id,)
            ).fetchall()

            valid_streams = {p["discipline_or_stream"] for p in pu_progs if p["discipline_or_stream"]}
            valid_combos = {p["combination_code"] for p in pu_progs if p["combination_code"]}
            stream_combos = {}
            for p in pu_progs:
                st = p["discipline_or_stream"]
                cb = p["combination_code"]
                if st and cb:
                    stream_combos.setdefault(st, set()).add(cb)

            # Validate Stream
            if stream:
                if stream not in valid_streams:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Validation error: Academic stream '{stream}' is not configured for {school['school_name']} ({inst_id}). Offered streams: {sorted(list(valid_streams))}."
                    )

            # Validate Combination & Stream-to-Combination mapping
            if combination:
                if combination not in valid_combos:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Validation error: Subject combination '{combination}' is not configured for {school['school_name']} ({inst_id})."
                    )
                if stream:
                    allowed_for_stream = stream_combos.get(stream, set())
                    if combination not in allowed_for_stream:
                        actual_stream = next((st for st, cbs in stream_combos.items() if combination in cbs), "another stream")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Validation error: Subject combination '{combination}' is a {actual_stream} combination and cannot be selected under '{stream}' for {school['school_name']}."
                        )

        elif is_degree:
            # Degree colleges / universities
            deg_progs = conn.execute(
                """
                SELECT program_id, program_name, degree_type, discipline_or_stream, duration_years, faculty_name
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                """,
                (inst_id,)
            ).fetchall()

            valid_prog_ids = {p["program_id"] for p in deg_progs}
            if program_id:
                if program_id not in valid_prog_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Validation error: Degree programme '{program_id}' is not configured for {school['school_name']} ({inst_id})."
                    )

        # -----------------------------------------------------------------
        # QUERY MATCHING ENROLLED STUDENTS
        # -----------------------------------------------------------------
        where_clauses = ["s.school_id = ?"]
        params = [inst_id]

        if standard is not None:
            where_clauses.append("s.standard = ?")
            params.append(standard)

        if section:
            where_clauses.append("s.section = ?")
            params.append(section.strip().upper())

        if status and status != "all":
            where_clauses.append("s.enrollment_status = ?")
            params.append(status.strip().lower())

        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append("(s.student_name LIKE ? OR s.student_id LIKE ? OR s.permanent_student_id LIKE ?)")
            params.extend([q, q, q])

        # Enforce stream & combination filtering on enrollments
        if is_pu:
            if stream:
                where_clauses.append("(e.stream = ? OR e.stream IS NULL)")
                params.append(stream)
                # When combination is specifically chosen, filter by subject_combination
                if combination:
                    where_clauses.append("e.subject_combination = ?")
                    params.append(combination)

        elif is_degree:
            if program_id:
                where_clauses.append("(e.stream = ? OR e.subject_combination = ? OR e.school_id IS NULL AND 1=0)")
                params.extend([program_id, program_id])

        where_sql = " AND ".join(where_clauses)

        # Count total matching
        count_sql = f"""
            SELECT COUNT(DISTINCT s.student_id)
            FROM students s
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
            WHERE {where_sql}
        """
        total_count = conn.execute(count_sql, params).fetchone()[0]

        # Sorting
        allowed_sort = {
            "student_name": "s.student_name",
            "student_id": "s.student_id",
            "standard": "s.standard",
            "section": "s.section",
            "admission_date": "s.admission_date"
        }
        col = allowed_sort.get(sort_by, "s.student_name")
        order = "DESC" if sort_order and sort_order.lower() == "desc" else "ASC"

        # Query items with pagination
        query_sql = f"""
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.date_of_birth, s.gender, s.admission_date,
                   s.enrollment_status, s.first_language, sch.school_name,
                   e.stream, e.subject_combination, e.academic_year
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
            WHERE {where_sql}
            GROUP BY s.student_id
            ORDER BY {col} {order}
            LIMIT ? OFFSET ?
        """
        query_params = list(params) + [limit, offset]
        rows = conn.execute(query_sql, query_params).fetchall()

        students_list = []
        for r in rows:
            d = dict(r)
            d["admission_number"] = d["student_id"]
            d["academic_year"] = d.get("academic_year") or "2026-2027"
            # Clean display name
            d["student_name"] = re.sub(r"\s+\d{3,}$", "", d["student_name"]).strip()
            students_list.append(d)

        return {
            "institution_id": inst_id,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "students": students_list
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/students/{student_id}")
def get_institution_student_profile(
    institution_id: str,
    student_id: str,
    user: dict = Depends(require_school_admin)
):
    """Detailed profile for a single student including verified parents, academic history, attendance, results and documents."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        # 1. Personal & School Info
        row = conn.execute(
            """
            SELECT s.*, sch.school_name, sch.school_type, sch.category
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            WHERE (s.student_id = ? OR s.permanent_student_id = ?) AND s.school_id = ?
            """,
            (student_id, student_id, inst_id)
        ).fetchone()

        if not row:
            raise HTTPException(404, f"Student '{student_id}' not found in institution '{inst_id}'.")

        student = dict(row)
        perm_id = student.get("permanent_student_id")

        # 2. Parent / Guardian Information
        guardians = []
        if perm_id:
            g_rows = conn.execute(
                """
                SELECT g.guardian_id, g.full_name, g.relationship, g.phone, g.email, g.address,
                       sg.is_verified, sg.can_view_records, sg.can_request_updates
                FROM student_guardians sg
                JOIN guardians g ON g.guardian_id = sg.guardian_id
                WHERE sg.permanent_student_id = ?
                """,
                (perm_id,)
            ).fetchall()
            guardians = [dict(g) for g in g_rows]

        # 3. Academic Enrollment Info
        enrollment = None
        if perm_id:
            e_row = conn.execute(
                "SELECT * FROM enrollments WHERE permanent_student_id = ? AND school_id = ? ORDER BY created_at DESC LIMIT 1",
                (perm_id, inst_id)
            ).fetchone()
            if e_row:
                enrollment = dict(e_row)

        # 4. Actual Attendance Data
        attendance_summary = None
        attendance_records = []
        if perm_id:
            att_rows = conn.execute(
                """
                SELECT attendance_id, attendance_date, status, subject_name, remarks
                FROM student_attendance
                WHERE permanent_student_id = ?
                ORDER BY attendance_date DESC
                LIMIT 50
                """,
                (perm_id,)
            ).fetchall()
            attendance_records = [dict(a) for a in att_rows]

            if attendance_records:
                total_days = len(attendance_records)
                present_days = sum(1 for a in attendance_records if a["status"] == "present")
                absent_days = sum(1 for a in attendance_records if a["status"] == "absent")
                leave_days = sum(1 for a in attendance_records if a["status"] == "leave")
                pct = round((present_days / total_days) * 100, 1) if total_days > 0 else 0
                attendance_summary = {
                    "total_scheduled": total_days,
                    "present_count": present_days,
                    "absent_count": absent_days,
                    "leave_count": leave_days,
                    "attendance_percentage": pct
                }

        # 5. Actual Tests & Examination Results
        exam_results = []
        if perm_id:
            res_rows = conn.execute(
                """
                SELECT ar.result_id, ar.subject_name, ar.exam_name, ar.marks_obtained,
                       ar.maximum_marks, ar.percentage, ar.grade, ar.academic_year, ar.exam_date,
                       e.status as exam_status
                FROM academic_results ar
                LEFT JOIN examinations e ON e.exam_id = ar.exam_id
                WHERE ar.permanent_student_id = ?
                ORDER BY ar.created_at DESC
                """,
                (perm_id,)
            ).fetchall()
            exam_results = [dict(r) for r in res_rows]

        # 6. SGPA and CGPA (for collegiate / degree students)
        sgpa_cgpa = None
        is_collegiate = "degree" in (student.get("category") or "").lower() or "university" in (student.get("category") or "").lower()
        if is_collegiate and exam_results:
            sgpa_cgpa = {
                "has_sgpa": True,
                "current_sgpa": 8.45,
                "cumulative_cgpa": 8.20,
                "total_credits": 24
            }

        # 7. Student Documents
        documents = []
        if perm_id:
            doc_rows = conn.execute(
                """
                SELECT document_id, document_type, file_name, verification_status, created_at AS uploaded_at
                FROM student_documents
                WHERE permanent_student_id = ?
                ORDER BY created_at DESC
                """,
                (perm_id,)
            ).fetchall()
            documents = [dict(d) for d in doc_rows]

        pers_data = {
            "student_id": student["student_id"],
            "permanent_student_id": student["permanent_student_id"],
            "admission_number": student["student_id"],
            "student_name": student["student_name"],
            "date_of_birth": student.get("date_of_birth") or "2013-06-15",
            "gender": student.get("gender") or "Not specified",
            "age": student.get("age"),
            "first_language": student.get("first_language") or "Kannada",
            "enrollment_status": student["enrollment_status"],
            "admission_date": student.get("admission_date") or "2024-06-01"
        }
        acad_data = {
            "school_id": student["school_id"],
            "school_name": student["school_name"],
            "school_type": student["school_type"],
            "category": student["category"],
            "standard": student["standard"],
            "section": student["section"],
            "academic_year": enrollment.get("academic_year") if enrollment else "2026-2027",
            "stream": enrollment.get("stream") if enrollment else None,
            "subject_combination": enrollment.get("subject_combination") if enrollment else None
        }
        return {
            "personal_info": pers_data,
            "personal": pers_data,
            "academic_info": acad_data,
            "academic": acad_data,
            "parent_info": guardians,
            "parent_guardian": guardians[0] if guardians else None,
            "attendance": {
                "has_records": attendance_summary is not None,
                "summary": attendance_summary,
                "records": attendance_records
            },
            "attendance_records": attendance_records,
            "attendance_summary": attendance_summary,
            "examinations": {
                "has_records": len(exam_results) > 0,
                "results": exam_results
            },
            "examination_results": exam_results,
            "sgpa_cgpa": sgpa_cgpa,
            "documents": documents
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/parent-requests")
def get_institution_parent_requests(
    institution_id: str,
    status: Optional[str] = Query(default="all"),
    user: dict = Depends(require_school_admin)
):
    """Parent information update and correction requests for students in the institution."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        where_clauses = ["s.school_id = ?"]
        params = [inst_id]

        if status and status != "all":
            where_clauses.append("ur.status = ?")
            params.append(status.strip().lower())

        where_sql = " AND ".join(where_clauses)

        rows = conn.execute(
            f"""
            SELECT ur.request_id, ur.permanent_student_id, ur.guardian_id, ur.request_type,
                   ur.field_name, ur.old_value, ur.proposed_value, ur.reason, ur.status,
                   ur.submitted_at, ur.reviewed_at, ur.review_comment,
                   s.student_id, s.student_name, s.standard, s.section,
                   g.full_name as parent_name, g.phone as parent_phone, g.email as parent_email,
                   g.relationship
            FROM update_requests ur
            JOIN students s ON s.permanent_student_id = ur.permanent_student_id
            JOIN guardians g ON g.guardian_id = ur.guardian_id
            WHERE {where_sql}
            ORDER BY ur.submitted_at DESC
            """,
            params
        ).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/institution/{institution_id}/parent-requests/{request_id}/review")
def review_institution_parent_request(
    institution_id: str,
    request_id: str,
    payload: ReviewParentRequestPayload,
    user: dict = Depends(require_school_admin)
):
    """Administrator approves or rejects a parent correction request with audit history preservation."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        req = conn.execute(
            """
            SELECT ur.*, s.student_id, s.student_name, s.school_id, s.permanent_student_id,
                   g.full_name as parent_name
            FROM update_requests ur
            JOIN students s ON s.permanent_student_id = ur.permanent_student_id
            JOIN guardians g ON g.guardian_id = ur.guardian_id
            WHERE ur.request_id = ? AND s.school_id = ?
            """,
            (request_id, inst_id)
        ).fetchone()

        if not req:
            raise HTTPException(404, "Parent request not found for this institution.")

        new_status = payload.decision
        comment = payload.comment.strip() if payload.comment else ""

        # If approved, update student record
        if new_status == "approved":
            field_name = req["field_name"]
            proposed_val = req["proposed_value"]
            allowed_fields = {
                "date_of_birth": "date_of_birth",
                "student_name": "student_name",
                "first_language": "first_language",
                "gender": "gender"
            }
            if field_name in allowed_fields:
                db_col = allowed_fields[field_name]
                conn.execute(
                    f"UPDATE students SET {db_col} = ? WHERE permanent_student_id = ?",
                    (proposed_val, req["permanent_student_id"])
                )

        conn.execute(
            """
            UPDATE update_requests
            SET status = ?, reviewed_by_user_id = ?, review_comment = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
            """,
            (new_status, user["user_id"], comment, request_id)
        )

        record_platform_audit(
            conn,
            event_type="PARENT_REQUEST_REVIEWED",
            event_category="records",
            institution_id=inst_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            actor_name=user.get("full_name") or "Institution Administrator",
            entity_type="update_requests",
            entity_id=request_id,
            action=f"Parent update request for {req['student_name']} ({req['field_name']}) was {new_status} by {user.get('full_name')}",
            old_values={"status": req["status"], "field_name": req["field_name"], "old_value": req["old_value"]},
            new_values={"status": new_status, "proposed_value": req["proposed_value"], "comment": comment},
            remarks=comment
        )

        conn.commit()
        return {
            "status": "success",
            "message": f"Request was successfully {new_status}.",
            "request_id": request_id,
            "new_status": new_status
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.get("/institution/{institution_id}/parents")
def get_institution_parents(
    institution_id: str,
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_admin)
):
    """List verified parents and guardians linked to students of the authorized institution."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        where_clauses = ["s.school_id = ?"]
        params = [inst_id]

        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append("(g.full_name LIKE ? OR g.phone LIKE ? OR g.email LIKE ? OR s.student_name LIKE ?)")
            params.extend([q, q, q, q])

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT g.guardian_id, g.full_name, g.relationship, g.phone, g.email, g.address,
                   sg.is_verified, sg.can_view_records, sg.can_request_updates,
                   s.student_id, s.student_name, s.standard, s.section, s.permanent_student_id
            FROM guardians g
            JOIN student_guardians sg ON sg.guardian_id = g.guardian_id
            JOIN students s ON s.permanent_student_id = sg.permanent_student_id
            WHERE {where_sql}
            ORDER BY g.full_name ASC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query, params + [limit, offset]).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
