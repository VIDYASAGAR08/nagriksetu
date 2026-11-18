backend_path = 'C:/Users/callm/nagriksetu/backend/main.py'
with open(backend_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update StudentRegisterRequest around line 135
old_model = """class StudentRegisterRequest(BaseModel):
    student_identifier: str = Field(min_length=3, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    email: Optional[str] = Field(default=None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    phone: Optional[str] = Field(default=None, pattern=r"^[6-9]\d{9}$")
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("student_identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 3:
            raise ValueError("Student identifier must contain at least 3 characters.")
        return s

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Full name must contain at least 2 characters.")
        return s"""

new_model = """class StudentLookupRequest(BaseModel):
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
        return v"""

# 2. Add /auth/student/lookup and update /auth/student/register around line 842
old_register_fn = """@app.post("/auth/student/register", response_model=StudentRegisterResponse, status_code=201)
def register_student_account(payload: StudentRegisterRequest):
    \"\"\"
    Dedicated on-demand student account activation and provisioning.
    Verifies that the student exists in the official students database,
    verifies name matches, confirms that no student user is already linked,
    and creates the student user account with role='student' and Argon2id hash.
    \"\"\"
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
    email_clean = payload.email.strip().lower() if payload.email else f"student.{identifier.lower()}@nagriksetu.portal"

    conn = get_connection()
    try:
        # 1. Look up student in students table
        student = conn.execute(
            \"\"\"
            SELECT student_id, student_name, school_id, standard, section,
                   permanent_student_id, enrollment_status
            FROM students
            WHERE student_id = ? COLLATE NOCASE OR permanent_student_id = ? COLLATE NOCASE
            \"\"\",
            (identifier, identifier),
        ).fetchone()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No enrolled student record found matching '{identifier}'. Please check your Student ID / Permanent Student ID.",
            )

        # Enforce name verification against official enrolled record
        submitted_name = " ".join(payload.full_name.strip().split()).lower()
        official_name = " ".join(student["student_name"].strip().split()).lower()
        if submitted_name != official_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The student name provided ('{payload.full_name.strip()}') does not match the official enrolled record for Student ID '{identifier}'.",
            )

        # 2. Check if student portal account is already registered
        existing_user = conn.execute(
            \"\"\"
            SELECT user_id FROM users
            WHERE student_id = ? OR permanent_student_id = ?
            \"\"\",
            (student["student_id"], student["permanent_student_id"]),
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student account has already been registered for student '{student['student_name']}' (ID: {student['student_id']}). Please sign in using your credentials or reset your password.",
            )

        # 3. Check email uniqueness
        existing_email = conn.execute(
            "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
            (email_clean,),
        ).fetchone()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists.",
            )

        # 4. Hash password with Argon2id
        try:
            pwd_hash = hash_password(payload.password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

        user_id = str(uuid.uuid4())
        conn.execute(
            \"\"\"
            INSERT INTO users (
                user_id, email, phone, password_hash, role,
                school_id, is_active, status, full_name,
                permanent_student_id, student_id, created_at
            ) VALUES (?, ?, ?, ?, 'student', ?, 1, 'active', ?, ?, ?, CURRENT_TIMESTAMP)
            \"\"\",
            (
                user_id,
                email_clean,
                payload.phone,
                pwd_hash,
                student["school_id"],
                student["student_name"],
                student["permanent_student_id"],
                student["student_id"],
            ),
        )
        conn.commit()

        return {
            "user_id": user_id,
            "student_id": student["student_id"],
            "permanent_student_id": student["permanent_student_id"],
            "full_name": student["student_name"],
            "school_id": student["school_id"],
            "message": "Student account activated successfully! You can now sign in using your credentials.",
        }
    finally:
        conn.close()"""

new_register_fn = """@app.post("/auth/student/lookup")
def lookup_student_for_activation(payload: StudentLookupRequest):
    \"\"\"
    Looks up an enrolled student record by Student ID or Permanent SATS ID
    prior to account activation. Returns verified official student details
    for student confirmation and identity verification.
    \"\"\"
    identifier = payload.student_identifier.strip()
    conn = get_connection()
    try:
        student = conn.execute(
            \"\"\"
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.enrollment_status, s.date_of_birth,
                   s.first_language, s.gender,
                   sch.school_name, sch.school_type, sch.district
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            WHERE s.student_id = ? COLLATE NOCASE OR s.permanent_student_id = ? COLLATE NOCASE
            \"\"\",
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student exists but is not actively enrolled (Current status: {student['enrollment_status']}). Activation is permitted only for actively enrolled students.",
            )

        # Error 3: Student account already activated
        existing_user = conn.execute(
            \"\"\"
            SELECT user_id, full_name FROM users
            WHERE student_id = ? OR permanent_student_id = ?
            \"\"\",
            (student["student_id"], student["permanent_student_id"]),
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student account already activated. An active portal account is already registered for this student. Please sign in with your credentials or reset your password.",
            )

        # Error 5: Student record requires institution verification
        if not student["date_of_birth"] or not str(student["date_of_birth"]).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student record requires institution verification. Official date of birth is missing from school records. Please contact your institution administrator to update your student profile.",
            )

        # Clean official name
        clean_name = re.sub(r"\\s+\\d{3,}$", "", student["student_name"]).strip()
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
    \"\"\"
    Dedicated on-demand student account activation and provisioning.
    Verifies that the student exists in the official students database,
    verifies identity via authorized verification method (Date of Birth),
    confirms active enrollment and no existing account,
    and provisions the user with role='student' and Argon2id hash.
    \"\"\"
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
            \"\"\"
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.enrollment_status, s.date_of_birth,
                   sch.school_name
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            WHERE s.student_id = ? COLLATE NOCASE OR s.permanent_student_id = ? COLLATE NOCASE
            \"\"\",
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student exists but is not actively enrolled (Current status: {student['enrollment_status']}). Activation is permitted only for actively enrolled students.",
            )

        # Error 3: Student account already activated
        existing_user = conn.execute(
            \"\"\"
            SELECT user_id FROM users
            WHERE student_id = ? OR permanent_student_id = ?
            \"\"\",
            (student["student_id"], student["permanent_student_id"]),
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student account already activated. An active portal account is already registered for this student. Please sign in with your credentials or reset your password.",
            )

        # Error 5: Student record requires institution verification
        if not student["date_of_birth"] or not str(student["date_of_birth"]).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student record requires institution verification. Official date of birth is missing from school records. Please contact your institution administrator to update your student profile.",
            )

        # Error 4: Identity verification failed (via Date of Birth)
        def _norm_dob(val: Optional[str]) -> str:
            if not val:
                return ""
            s = val.strip()
            m1 = re.match(r"^(\\d{4})[-/](\\d{1,2})[-/](\\d{1,2})$", s)
            if m1:
                return f"{int(m1.group(1)):04d}-{int(m1.group(2)):02d}-{int(m1.group(3)):02d}"
            m2 = re.match(r"^(\\d{1,2})[-/](\\d{1,2})[-/](\\d{4})$", s)
            if m2:
                return f"{int(m2.group(3)):04d}-{int(m2.group(2)):02d}-{int(m2.group(1)):02d}"
            return s

        if not payload.date_of_birth or not payload.date_of_birth.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identity verification failed. Official Date of Birth is required to confirm student identity.",
            )

        provided_dob = _norm_dob(payload.date_of_birth)
        official_dob = _norm_dob(student["date_of_birth"])
        if provided_dob != official_dob:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identity verification failed. The provided date of birth does not match official institution records for this student.",
            )

        # Official clean student name (do not trust user-entered spelling)
        clean_name = re.sub(r"\\s+\\d{3,}$", "", student["student_name"]).strip()
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
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email address already exists. Please provide a different email or leave it blank.",
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
        conn.execute(
            \"\"\"
            INSERT INTO users (
                user_id, email, phone, password_hash, role,
                school_id, is_active, status, full_name,
                permanent_student_id, student_id, created_at
            ) VALUES (?, ?, ?, ?, 'student', ?, 1, 'active', ?, ?, ?, CURRENT_TIMESTAMP)
            \"\"\",
            (
                user_id,
                email_clean,
                payload.phone.strip() if payload.phone else None,
                pwd_hash,
                student["school_id"],
                clean_name,
                student["permanent_student_id"],
                student["student_id"],
            ),
        )

        # Record audit log
        audit_id = str(uuid.uuid4())
        conn.execute(
            \"\"\"
            INSERT INTO audit_logs (
                audit_id, actor_user_id, actor_role,
                action, entity_type, entity_id,
                school_id, ip_address, metadata_json
            ) VALUES (?, ?, 'student', 'STUDENT_ACCOUNT_ACTIVATED', 'user', ?, ?, NULL, ?)
            \"\"\",
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
        conn.close()"""

for old, new, label in [
    (old_model, new_model, "StudentLookupRequest and StudentRegisterRequest"),
    (old_register_fn, new_register_fn, "lookup_student_for_activation and register_student_account")
]:
    old_crlf = old.replace('\n', '\r\n')
    new_crlf = new.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf, 1)
        print(f"Replaced CRLF: {label}")
    elif old in text:
        text = text.replace(old, new, 1)
        print(f"Replaced LF: {label}")
    else:
        print(f"FAILED to find: {label}")

with open(backend_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated backend/main.py successfully.")
