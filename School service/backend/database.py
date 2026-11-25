
import json
import os
import sqlite3
import uuid

DATABASE_NAME = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "nagriksetu.db"),
)


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def add_column_if_missing(connection, table, column, definition):
    existing = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table})")
    }
    if column not in existing:
        connection.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def create_tables():
    database_directory = os.path.dirname(os.path.abspath(DATABASE_NAME))
    os.makedirs(database_directory, exist_ok=True)

    connection = get_connection()

    try:
        with connection:
            # Preserve the existing schools table and its records.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    school_id TEXT PRIMARY KEY,
                    school_name TEXT NOT NULL,
                    district TEXT NOT NULL,
                    state TEXT NOT NULL,
                    school_type TEXT NOT NULL
                )
            """)

            # Preserve the existing students table and its records.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    student_name TEXT NOT NULL,
                    school_id TEXT NOT NULL,
                    standard INTEGER NOT NULL,
                    section TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(school_id)
                )
            """)

            # Additional school information for the public directory.
            school_columns = {
                "address": "TEXT",
                "established_year": "INTEGER",
                "description": "TEXT",
                "public_phone": "TEXT",
                "website": "TEXT",
                "facilities_json": "TEXT NOT NULL DEFAULT '[]'",
            }
            for column, definition in school_columns.items():
                add_column_if_missing(
                    connection, "schools", column, definition
                )

            # Stable internal identity, separate from the displayed school ID.
            student_columns = {
                "permanent_student_id": "TEXT",
                "first_language": "TEXT",
                "date_of_birth": "TEXT",
                "gender": "TEXT",
                "admission_date": "TEXT",
                "enrollment_status": "TEXT NOT NULL DEFAULT 'active'",
                "blood_group": "TEXT",
                "social_category": "TEXT",
                "address": "TEXT",
                "district": "TEXT",
                "state": "TEXT NOT NULL DEFAULT 'Karnataka'",
                "pincode": "TEXT",
                "contact_number": "TEXT",
                "student_email": "TEXT",
                "roll_number": "TEXT",
                "medium_of_instruction": "TEXT",
                "aadhaar_masked": "TEXT",
                "is_synthetic_demo": "INTEGER NOT NULL DEFAULT 1",
            }
            for column, definition in student_columns.items():
                add_column_if_missing(
                    connection, "students", column, definition
                )

            # Give existing students stable identifiers without changing
            # their existing student_id values.
            existing_students = connection.execute("""
                SELECT student_id
                FROM students
                WHERE permanent_student_id IS NULL
                   OR permanent_student_id = ''
            """).fetchall()

            for student in existing_students:
                connection.execute(
                    """
                    UPDATE students
                    SET permanent_student_id = ?
                    WHERE student_id = ?
                    """,
                    (
                        "NS-" + uuid.uuid4().hex.upper(),
                        student["student_id"],
                    ),
                )

            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_students_permanent_id
                ON students(permanent_student_id)
            """)

            # Login identities. Passwords must be securely hashed by the
            # authentication layer; never store plain-text passwords.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (
                        role IN ('parent', 'school_staff', 'school_admin')
                    ),
                    school_id TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(school_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS guardians (
                    guardian_id TEXT PRIMARY KEY,
                    user_id TEXT UNIQUE,
                    full_name TEXT NOT NULL,
                    relationship TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    address TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_guardians (
                    student_guardian_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    guardian_id TEXT NOT NULL,
                    can_view_records INTEGER NOT NULL DEFAULT 1,
                    can_request_updates INTEGER NOT NULL DEFAULT 1,
                    is_verified INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (permanent_student_id, guardian_id),
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (guardian_id) REFERENCES guardians(guardian_id)
                )
            """)

            # One record per school enrollment period. Previous enrollments
            # are retained when a student transfers.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    school_id TEXT NOT NULL,
                    academic_year TEXT NOT NULL,
                    standard INTEGER NOT NULL CHECK (standard BETWEEN 1 AND 12),
                    section TEXT NOT NULL CHECK (section IN ('A', 'B', 'C')),
                    first_language TEXT NOT NULL CHECK (
                        first_language IN ('Kannada', 'Hindi', 'Sanskrit')
                    ),
                    stream TEXT,
                    subject_combination TEXT,
                    admission_date TEXT,
                    leaving_date TEXT,
                    enrollment_status TEXT NOT NULL DEFAULT 'active'
                        CHECK (enrollment_status IN (
                            'active', 'completed', 'transferred', 'withdrawn'
                        )),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (school_id) REFERENCES schools(school_id),
                    UNIQUE (permanent_student_id, school_id, academic_year)
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_enrollments_student
                ON enrollments(permanent_student_id, academic_year)
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS academic_results (
                    result_id TEXT PRIMARY KEY,
                    enrollment_id TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    exam_name TEXT NOT NULL,
                    marks_obtained REAL NOT NULL CHECK (marks_obtained >= 0),
                    maximum_marks REAL NOT NULL CHECK (maximum_marks > 0),
                    academic_year TEXT NOT NULL,
                    exam_date TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (enrollment_id)
                        REFERENCES enrollments(enrollment_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_documents (
                    document_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    enrollment_id TEXT,
                    document_type TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    private_storage_key TEXT NOT NULL,
                    uploaded_by_user_id TEXT,
                    verified_by_user_id TEXT,
                    verification_status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (verification_status IN (
                            'pending', 'verified', 'rejected'
                        )),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (enrollment_id)
                        REFERENCES enrollments(enrollment_id),
                    FOREIGN KEY (uploaded_by_user_id)
                        REFERENCES users(user_id),
                    FOREIGN KEY (verified_by_user_id)
                        REFERENCES users(user_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS fees (
                    fee_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    school_id TEXT NOT NULL,
                    academic_year TEXT NOT NULL,
                    fee_type TEXT NOT NULL,
                    amount_due REAL NOT NULL CHECK (amount_due >= 0),
                    amount_paid REAL NOT NULL DEFAULT 0 CHECK (amount_paid >= 0),
                    due_date TEXT,
                    payment_status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (payment_status IN (
                            'pending', 'partially_paid', 'paid', 'waived'
                        )),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (school_id) REFERENCES schools(school_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS scholarships (
                    scholarship_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    scholarship_name TEXT NOT NULL,
                    eligibility_status TEXT NOT NULL DEFAULT 'not_assessed'
                        CHECK (eligibility_status IN (
                            'not_assessed', 'eligible', 'ineligible', 'needs_review'
                        )),
                    application_status TEXT NOT NULL DEFAULT 'not_applied'
                        CHECK (application_status IN (
                            'not_applied', 'submitted', 'under_review',
                            'approved', 'rejected'
                        )),
                    academic_year TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS update_requests (
                    request_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    guardian_id TEXT NOT NULL,
                    request_type TEXT NOT NULL CHECK (
                        request_type IN ('request_change', 'report_change')
                    ),
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    proposed_value TEXT NOT NULL,
                    reason TEXT,
                    supporting_document_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN (
                            'pending', 'approved', 'rejected', 'cancelled'
                        )),
                    reviewed_by_user_id TEXT,
                    review_comment TEXT,
                    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TEXT,
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (guardian_id) REFERENCES guardians(guardian_id),
                    FOREIGN KEY (supporting_document_id)
                        REFERENCES student_documents(document_id),
                    FOREIGN KEY (reviewed_by_user_id)
                        REFERENCES users(user_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS school_transfers (
                    transfer_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    previous_enrollment_id TEXT,
                    new_enrollment_id TEXT,
                    requested_by_guardian_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN (
                            'pending', 'approved', 'rejected', 'completed'
                        )),
                    reason TEXT,
                    requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by_user_id TEXT,
                    reviewed_at TEXT,
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (previous_enrollment_id)
                        REFERENCES enrollments(enrollment_id),
                    FOREIGN KEY (new_enrollment_id)
                        REFERENCES enrollments(enrollment_id),
                    FOREIGN KEY (requested_by_guardian_id)
                        REFERENCES guardians(guardian_id),
                    FOREIGN KEY (reviewed_by_user_id)
                        REFERENCES users(user_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS school_programs (
                    program_id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    standard INTEGER NOT NULL CHECK (standard BETWEEN 1 AND 12),
                    section TEXT CHECK (section IN ('A', 'B', 'C')),
                    first_language TEXT CHECK (
                        first_language IN ('Kannada', 'Hindi', 'Sanskrit')
                    ),
                    stream TEXT,
                    subject_combination TEXT,
                    is_available INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (school_id) REFERENCES schools(school_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS school_achievements (
                    achievement_id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    achievement_date TEXT,
                    public_document_url TEXT,
                    is_published INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (school_id) REFERENCES schools(school_id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS school_change_log (
                    log_id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    permanent_student_id TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by_user_id TEXT,
                    change_reason TEXT,
                    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(school_id),
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id),
                    FOREIGN KEY (changed_by_user_id)
                        REFERENCES users(user_id)
                )
            """)

            # Phase 2B: Add linking_requests table for parent-child relationship requests
            connection.execute("""
                CREATE TABLE IF NOT EXISTS linking_requests (
                    request_id TEXT PRIMARY KEY,
                    parent_user_id TEXT NOT NULL,
                    school_id TEXT NOT NULL,
                    student_ref TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    verification_doc_id TEXT,
                    additional_notes TEXT,
                    request_status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (request_status IN (
                            'pending', 'approved', 'rejected', 'cancelled'
                        )),
                    reviewer_user_id TEXT,
                    reviewer_comment TEXT,
                    permanent_student_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TEXT,
                    CHECK (
                        request_status != 'approved'
                        OR permanent_student_id IS NOT NULL
                    ),
                    FOREIGN KEY (parent_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (school_id) REFERENCES schools(school_id),
                    FOREIGN KEY (reviewer_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (permanent_student_id)
                        REFERENCES students(permanent_student_id)
                )
            """)

            # Partial unique index to prevent duplicate pending requests for the same parent, school, and student reference
            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_linking_requests_pending_unique
                ON linking_requests(parent_user_id, school_id, student_ref)
                WHERE request_status = 'pending'
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_linking_requests_school_status
                ON linking_requests(school_id, request_status)
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_linking_requests_parent_status
                ON linking_requests(parent_user_id, request_status)
            """)

            # Phase 2B: Add audit_logs table for platform-wide security and activity logging
            connection.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    audit_id TEXT PRIMARY KEY,
                    actor_user_id TEXT,
                    actor_role TEXT,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    school_id TEXT,
                    ip_address TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (actor_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (school_id) REFERENCES schools(school_id)
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_actor
                ON audit_logs(actor_user_id, created_at)
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
                ON audit_logs(entity_type, entity_id)
            """)

            # Phase 18: Add platform_audit_logs table for Central Platform Monitoring & Audit Feed
            connection.execute("""
                CREATE TABLE IF NOT EXISTS platform_audit_logs (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    event_category TEXT NOT NULL,
                    institution_id TEXT,
                    actor_user_id TEXT,
                    actor_name TEXT,
                    actor_role TEXT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    action TEXT NOT NULL,
                    old_values TEXT,
                    new_values TEXT,
                    remarks TEXT,
                    request_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_pal_category ON platform_audit_logs(event_category)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_pal_institution ON platform_audit_logs(institution_id)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_pal_created_at ON platform_audit_logs(created_at DESC)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_pal_entity ON platform_audit_logs(entity_type, entity_id)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_pal_event_type ON platform_audit_logs(event_type)
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_school
                ON audit_logs(school_id, created_at)
            """)

            # Phase 12: Academic Management (Attendance, Examinations, Result Audits, Announcements)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS student_attendance (
                    attendance_id TEXT PRIMARY KEY,
                    institution_id TEXT NOT NULL,
                    permanent_student_id TEXT NOT NULL,
                    academic_year TEXT NOT NULL DEFAULT '2026-2027',
                    attendance_date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'leave')),
                    subject_name TEXT,
                    remarks TEXT,
                    recorded_by_user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (institution_id) REFERENCES schools(school_id),
                    FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id),
                    FOREIGN KEY (recorded_by_user_id) REFERENCES users(user_id)
                )
            """)
            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique
                ON student_attendance(institution_id, permanent_student_id, attendance_date, COALESCE(subject_name, ''))
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_attendance_student_date
                ON student_attendance(permanent_student_id, attendance_date)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_attendance_inst_date
                ON student_attendance(institution_id, attendance_date)
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS examinations (
                    exam_id TEXT PRIMARY KEY,
                    institution_id TEXT NOT NULL,
                    academic_year TEXT NOT NULL DEFAULT '2026-2027',
                    exam_name TEXT NOT NULL,
                    standard_or_level TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'ongoing', 'completed', 'cancelled')),
                    description TEXT,
                    created_by_user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (institution_id) REFERENCES schools(school_id),
                    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_examinations_inst
                ON examinations(institution_id, academic_year)
            """)

            add_column_if_missing(connection, "academic_results", "permanent_student_id", "TEXT")
            add_column_if_missing(connection, "academic_results", "exam_id", "TEXT")
            add_column_if_missing(connection, "academic_results", "grade", "TEXT")
            add_column_if_missing(connection, "academic_results", "percentage", "REAL")
            add_column_if_missing(connection, "academic_results", "recorded_by_user_id", "TEXT")
            add_column_if_missing(connection, "academic_results", "updated_at", "TEXT")
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_academic_results_perm_id
                ON academic_results(permanent_student_id)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_student_documents_perm_id
                ON student_documents(permanent_student_id)
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS academic_result_audits (
                    audit_id TEXT PRIMARY KEY,
                    result_id TEXT NOT NULL,
                    previous_marks REAL,
                    new_marks REAL,
                    previous_max_marks REAL,
                    new_max_marks REAL,
                    reason_for_change TEXT NOT NULL,
                    modified_by_user_id TEXT NOT NULL,
                    modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (result_id) REFERENCES academic_results(result_id),
                    FOREIGN KEY (modified_by_user_id) REFERENCES users(user_id)
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_result_audits
                ON academic_result_audits(result_id)
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS institution_announcements (
                    announcement_id TEXT PRIMARY KEY,
                    institution_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    target_audience TEXT NOT NULL DEFAULT 'all' CHECK(target_audience IN ('all', 'students', 'parents', 'staff')),
                    published_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_by_user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (institution_id) REFERENCES schools(school_id),
                    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_announcements_inst
                ON institution_announcements(institution_id)
            """)

            # Phase 2B: Add users.full_name column if missing and backfill parent names
            add_column_if_missing(connection, "users", "full_name", "TEXT")

            # Backfill parent names from guardians.full_name where available.
            # Other users (school staff/admin) remain NULL when their actual name is unknown.
            connection.execute("""
                UPDATE users
                SET full_name = (
                    SELECT g.full_name
                    FROM guardians g
                    WHERE g.user_id = users.user_id
                )
                WHERE users.full_name IS NULL
                  AND EXISTS (
                      SELECT 1
                      FROM guardians g
                      WHERE g.user_id = users.user_id
                  )
            """)

            # Backfill a current enrollment for each existing student.
            # This is a migration of existing records, not a reseed.
            existing_students = connection.execute("""
                SELECT s.student_id, s.permanent_student_id, s.school_id,
                       s.standard, s.section, s.admission_date,
                       s.enrollment_status
                FROM students s
                WHERE NOT EXISTS (
                    SELECT 1 FROM enrollments e
                    WHERE e.permanent_student_id = s.permanent_student_id
                      AND e.school_id = s.school_id
                      AND e.academic_year = '2026-2027'
                )
            """).fetchall()

            language_by_section = {
                "A": "Kannada",
                "B": "Hindi",
                "C": "Sanskrit",
            }

            for student in existing_students:
                section = student["section"]
                if section not in language_by_section:
                    raise ValueError(
                        f"Unexpected section {section!r} for "
                        f"student {student['student_id']}"
                    )

                connection.execute("""
                    INSERT INTO enrollments (
                        enrollment_id, permanent_student_id, school_id,
                        academic_year, standard, section, first_language,
                        admission_date, enrollment_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "ENR-" + uuid.uuid4().hex.upper(),
                    student["permanent_student_id"],
                    student["school_id"],
                    "2026-2027",
                    student["standard"],
                    section,
                    language_by_section[section],
                    student["admission_date"],
                    student["enrollment_status"],
                ))

            # JSON is used for flexible school facilities.
            # Validate its default format during initialization.
            connection.execute("""
                UPDATE schools
                SET facilities_json = '[]'
                WHERE facilities_json IS NULL OR facilities_json = ''
            """)

            # Add is_email_verified to users (defaults to 1 for existing users)
            add_column_if_missing(connection, "users", "is_email_verified", "INTEGER NOT NULL DEFAULT 1")

            # Email OTP verification table
            connection.execute("""
                CREATE TABLE IF NOT EXISTS email_otps (
                    otp_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    otp_hash TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 5,
                    is_used INTEGER DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ip_address TEXT
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_email_otps_lookup
                ON email_otps(email, purpose, is_used)
            """)

            # AI Question Bank table for NagrikSetu AI Assistant
            connection.execute("""
                CREATE TABLE IF NOT EXISTS ai_question_bank (
                    id TEXT PRIMARY KEY,
                    question_code TEXT UNIQUE NOT NULL,
                    question_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    intended_role TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    required_information TEXT,
                    data_source TEXT,
                    answer_method TEXT NOT NULL,
                    expected_answer TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_question_bank_code
                ON ai_question_bank(question_code)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_question_bank_category
                ON ai_question_bank(category)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_question_bank_role
                ON ai_question_bank(intended_role)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_question_bank_active
                ON ai_question_bank(is_active)
            """)
            # Institution Registration Applications table
            connection.execute("""
                CREATE TABLE IF NOT EXISTS institution_applications (
                    application_id TEXT PRIMARY KEY,
                    application_ref TEXT UNIQUE NOT NULL,
                    institution_id TEXT NOT NULL,
                    institution_name TEXT NOT NULL,
                    institution_type TEXT NOT NULL,
                    institution_category TEXT NOT NULL,
                    established_year INTEGER,
                    affiliation TEXT,
                    recognition TEXT,
                    address_line1 TEXT,
                    address_line2 TEXT,
                    city TEXT,
                    district TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'Karnataka',
                    pincode TEXT,
                    country TEXT NOT NULL DEFAULT 'India',
                    official_email TEXT NOT NULL,
                    official_phone TEXT NOT NULL,
                    website TEXT,
                    academic_info_json TEXT,
                    applicant_name TEXT NOT NULL,
                    applicant_designation TEXT NOT NULL,
                    applicant_email TEXT NOT NULL,
                    applicant_phone TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    review_comments TEXT,
                    reviewed_by TEXT,
                    reviewed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_inst_app_status
                ON institution_applications(status)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_inst_app_inst_id
                ON institution_applications(institution_id)
            """)

            # Institution-Issued Student Linking Codes table
            connection.execute("""
                CREATE TABLE IF NOT EXISTS institution_linking_codes (
                    code_id TEXT PRIMARY KEY,
                    permanent_student_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    institution_id TEXT NOT NULL,
                    parent_user_id TEXT,
                    code_hash TEXT NOT NULL,
                    plain_code TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 5,
                    is_used INTEGER NOT NULL DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id),
                    FOREIGN KEY (institution_id) REFERENCES schools(school_id)
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_inst_linking_codes_student
                ON institution_linking_codes(permanent_student_id, is_used)
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_inst_linking_codes_parent
                ON institution_linking_codes(parent_user_id, is_used)
            """)


            # Centralized Service Requests & Correction Management System
            connection.execute("""
                CREATE TABLE IF NOT EXISTS service_requests (
                    request_id TEXT PRIMARY KEY,
                    tracking_number TEXT UNIQUE,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    requester_user_id TEXT NOT NULL,
                    requester_role TEXT NOT NULL,
                    requester_name TEXT,
                    requester_email TEXT,
                    requester_phone TEXT,
                    affected_person_type TEXT DEFAULT 'self',
                    affected_student_id TEXT,
                    permanent_student_id TEXT,
                    affected_person_name TEXT,
                    institution_id TEXT,
                    target_module TEXT,
                    target_record_id TEXT,
                    field_name TEXT,
                    current_value TEXT,
                    requested_value TEXT,
                    status TEXT NOT NULL DEFAULT 'SUBMITTED',
                    routing_tier TEXT NOT NULL DEFAULT 'institution',
                    assigned_institution_id TEXT,
                    assigned_to_user_id TEXT,
                    rejection_reason TEXT,
                    clarification_prompt TEXT,
                    requester_response TEXT,
                    is_escalated INTEGER DEFAULT 0,
                    escalated_to TEXT,
                    escalated_at TEXT,
                    submitted_at TEXT DEFAULT (DATETIME('now', 'localtime')),
                    updated_at TEXT DEFAULT (DATETIME('now', 'localtime')),
                    resolved_at TEXT,
                    closed_at TEXT
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sr_requester ON service_requests(requester_user_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sr_inst ON service_requests(assigned_institution_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sr_status ON service_requests(status)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sr_student ON service_requests(permanent_student_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_sr_st_id ON service_requests(affected_student_id)")

            connection.execute("""
                CREATE TABLE IF NOT EXISTS request_attachments (
                    attachment_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    uploaded_by_user_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT,
                    file_size INTEGER,
                    file_url_or_path TEXT,
                    purpose TEXT DEFAULT 'supporting_document',
                    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
                    FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_ra_req ON request_attachments(request_id)")

            connection.execute("""
                CREATE TABLE IF NOT EXISTS request_remarks (
                    remark_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    author_user_id TEXT NOT NULL,
                    author_name TEXT NOT NULL,
                    author_role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    visibility TEXT NOT NULL DEFAULT 'requester_visible',
                    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
                    FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_rr_req ON request_remarks(request_id)")

            connection.execute("""
                CREATE TABLE IF NOT EXISTS request_status_history (
                    history_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor_user_id TEXT NOT NULL,
                    actor_name TEXT,
                    actor_role TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
                    FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_rsh_req ON request_status_history(request_id)")

            connection.execute("""
                CREATE TABLE IF NOT EXISTS request_corrections (
                    correction_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    target_record_id TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    previous_value TEXT,
                    corrected_value TEXT NOT NULL,
                    correction_reason TEXT NOT NULL,
                    administrator_id TEXT NOT NULL,
                    administrator_name TEXT,
                    administrator_role TEXT,
                    verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
                    verified_by_user_id TEXT,
                    verified_at TEXT,
                    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
                    FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_rc_req ON request_corrections(request_id)")

            connection.execute("""
                CREATE TABLE IF NOT EXISTS request_audit_logs (
                    audit_id TEXT PRIMARY KEY,
                    request_id TEXT,
                    actor_user_id TEXT,
                    actor_role TEXT,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    school_id TEXT,
                    details_json TEXT,
                    created_at TEXT DEFAULT (DATETIME('now', 'localtime'))
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_ral_req ON request_audit_logs(request_id)")

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
    print("NagrikSetu database schema created or upgraded successfully.")
