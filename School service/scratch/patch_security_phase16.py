import re

main_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Patch CORS and insert AuthRateLimiter
old_cors = """app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

new_cors_and_limiter = """cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    trusted_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
else:
    trusted_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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
    \"\"\"Thread-safe in-memory sliding window rate limiter for authentication endpoints.\"\"\"
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

auth_limiter = AuthRateLimiter()"""

assert old_cors in content, "old_cors not found in main.py"
content = content.replace(old_cors, new_cors_and_limiter)
print("[+] CORS and AuthRateLimiter patched")

# 2. Patch login with rate limiting and lockout
old_login_def = """@app.post("/auth/login", response_model=LoginResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    institution_id: Optional[str] = Query(default=None),
):
    \"\"\"Use the username field for an email address or phone number.\"\"\"
    identifier = form.username.strip()

    conn = get_connection()
    try:
        user = conn.execute(
            \"\"\"
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active, status, full_name,
                   permanent_student_id, student_id
            FROM users
            WHERE email = ? COLLATE NOCASE 
               OR phone = ?
               OR student_id = ? COLLATE NOCASE
               OR permanent_student_id = ? COLLATE NOCASE
            \"\"\",
            (identifier, identifier, identifier, identifier),
        ).fetchone()

        if (
            user is None
            or not user["is_active"]
            or user["status"] == "suspended"
            or not verify_password(form.password, user["password_hash"])
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )"""

new_login_def = """@app.post("/auth/login", response_model=LoginResponse)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    institution_id: Optional[str] = Query(default=None),
):
    \"\"\"Use the username field for an email address or phone number.\"\"\"
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
            \"\"\"
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active, status, full_name,
                   permanent_student_id, student_id
            FROM users
            WHERE email = ? COLLATE NOCASE 
               OR phone = ?
               OR student_id = ? COLLATE NOCASE
               OR permanent_student_id = ? COLLATE NOCASE
            \"\"\",
            (identifier, identifier, identifier, identifier),
        ).fetchone()

        if (
            user is None
            or not user["is_active"]
            or user["status"] == "suspended"
            or not verify_password(form.password, user["password_hash"])
        ):
            auth_limiter.record_failed_login(client_ip, identifier, max_failures=5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        auth_limiter.reset_failed_login(client_ip, identifier)"""

assert old_login_def in content, "old_login_def not found in main.py"
content = content.replace(old_login_def, new_login_def)
print("[+] Login rate limiting and brute force protection patched")

# 3. Patch check_admission_application_access helper right below get_optional_current_user
old_opt_user_end = """        try:
            row = conn.execute("SELECT user_id, phone, email, full_name, role, school_id, is_active FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception:
        return None"""

new_opt_user_end = """        try:
            row = conn.execute("SELECT user_id, phone, email, full_name, role, school_id, is_active FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception:
        return None


def check_admission_application_access(app_row: dict, user: Optional[dict]) -> bool:
    \"\"\"
    Verifies that the caller has legitimate authority over an admission application.
    Allowed actors:
    1. platform_admin: Statewide oversight.
    2. school_admin / staff: Only if reviewer's assigned school_id matches the application's institution_id.
    3. applicant / parent: Only if caller's user_id, phone, or email matches the application record.
    All others (unauthenticated or cross-tenant/unrelated users): Denied.
    \"\"\"
    if not user:
        return False
    role = user.get("role")
    if role == "platform_admin":
        return True
    if role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff"):
        return user.get("school_id") == app_row["institution_id"]
    if role == "parent":
        uid = user.get("user_id")
        uphone = user.get("phone")
        uemail = (user.get("email") or "").strip().lower()
        if uid and app_row.get("parent_user_id") and uid == app_row["parent_user_id"]:
            return True
        if uphone and app_row.get("parent_phone") and uphone == app_row["parent_phone"]:
            return True
        if uemail and app_row.get("parent_email") and uemail == str(app_row["parent_email"]).strip().lower():
            return True
    return False"""

assert old_opt_user_end in content, "old_opt_user_end not found in main.py"
content = content.replace(old_opt_user_end, new_opt_user_end)
print("[+] check_admission_application_access helper added")

# 4. Patch Stage 2 eligibility, submit, document upload, list documents, and get file
old_stage2_elig = """        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        app_data = dict(app_row)"""

new_stage2_elig = """        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        if not check_admission_application_access(dict(app_row), current_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if not current_user else status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to view this application's Stage 2 dossier.",
            )

        app_data = dict(app_row)"""

assert old_stage2_elig in content, "old_stage2_elig not found in main.py"
content = content.replace(old_stage2_elig, new_stage2_elig, 1)
print("[+] Stage 2 eligibility access control patched")

old_stage2_sub = """        app_row = conn.execute(
            "SELECT application_id, institution_id, status, applicant_name, parent_user_id, parent_phone FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        valid_entry_statuses"""

new_stage2_sub = """        app_row = conn.execute(
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

        valid_entry_statuses"""

assert old_stage2_sub in content, "old_stage2_sub not found in main.py"
content = content.replace(old_stage2_sub, new_stage2_sub, 1)
print("[+] Stage 2 submit access control patched")

old_doc_upload = """        app_row = conn.execute(
            "SELECT application_id, institution_id, status, applicant_name FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        # Decode base64 file data
        try:
            file_bytes = base64.b64decode(payload.file_data_base64)
        except Exception:
            raise HTTPException(400, "Invalid base64 document content.")

        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Document size exceeds the 10 MB limit.")"""

new_doc_upload = """        app_row = conn.execute(
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
        is_jpg = file_bytes.startswith(b"\\xff\\xd8\\xff")
        is_png = file_bytes.startswith(b"\\x89PNG\\r\\n\\x1a\\n")
        is_webp = len(file_bytes) > 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP"

        if not (is_pdf or is_jpg or is_png or is_webp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported or malicious file type. Only authentic PDF documents and JPEG/PNG/WEBP images are permitted.",
            )

        # Disallow dangerous executable extensions in filename
        disallowed_exts = (".exe", ".sh", ".bat", ".cmd", ".js", ".php", ".py", ".html", ".htm", ".vbs", ".ps1")
        if any(payload.file_name.lower().endswith(ext) for ext in disallowed_exts):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains an unacceptable or dangerous file extension.",
            )"""

assert old_doc_upload in content, "old_doc_upload not found in main.py"
content = content.replace(old_doc_upload, new_doc_upload, 1)
print("[+] Document upload access control and MIME/magic validation patched")

old_get_docs = """@app.get("/admissions/applications/{application_id}/documents")
def get_stage2_documents(
    application_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    \"\"\"
    Returns list of uploaded documents and their verification status for an application.
    \"\"\"
    conn = get_connection()
    try:
        rows = conn.execute("""

new_get_docs = """@app.get("/admissions/applications/{application_id}/documents")
def get_stage2_documents(
    application_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    \"\"\"
    Returns list of uploaded documents and their verification status for an application.
    \"\"\"
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

        rows = conn.execute("""

assert old_get_docs in content, "old_get_docs not found in main.py"
content = content.replace(old_get_docs, new_get_docs, 1)
print("[+] List documents authorization patched")

old_get_file = """@app.get("/admissions/applications/{application_id}/documents/{document_id}/file")
def get_admission_document_file(
    application_id: str,
    document_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    \"\"\"
    Retrieves the raw document file for viewing/download.
    \"\"\"
    conn = get_connection()
    try:
        doc = conn.execute("""

new_get_file = """@app.get("/admissions/applications/{application_id}/documents/{document_id}/file")
def get_admission_document_file(
    application_id: str,
    document_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    \"\"\"
    Retrieves the raw document file for viewing/download.
    \"\"\"
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

        doc = conn.execute("""

assert old_get_file in content, "old_get_file not found in main.py"
content = content.replace(old_get_file, new_get_file, 1)
print("[+] Get document file authorization patched")

# 5. Patch examinations multi-tenant boundary
old_exams_def = """@app.get("/academic/examinations")
def list_examinations(
    institution_id: Optional[str] = None,
    academic_year: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    \"\"\"
    Lists scheduled and past examinations.
    \"\"\""""

new_exams_def = """@app.get("/academic/examinations")
def list_examinations(
    institution_id: Optional[str] = None,
    academic_year: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    \"\"\"
    Lists scheduled and past examinations.
    Enforces multi-institution boundaries for staff and administrators.
    \"\"\"
    if current_user and current_user.get("role") != "platform_admin":
        user_school = current_user.get("school_id")
        if user_school:
            if institution_id and institution_id.strip() != user_school:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: You cannot view examinations for institution '{institution_id}'.",
                )
            institution_id = user_school"""

assert old_exams_def in content, "old_exams_def not found in main.py"
content = content.replace(old_exams_def, new_exams_def, 1)
print("[+] Examinations multi-tenant boundary patched")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSuccessfully applied all Phase 16 security patches to main.py!")
