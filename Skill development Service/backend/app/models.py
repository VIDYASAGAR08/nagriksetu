from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(190), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(40), default="CITIZEN", index=True, nullable=False) # CITIZEN, SKILL_DEPARTMENT_ADMIN
    citizen_ref = Column(String(80), unique=True, index=True, nullable=True) # e.g. CIT-100234
    full_name = Column(String(180), nullable=True)
    phone = Column(String(30), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(24), unique=True, index=True, nullable=False) # CAT-0001
    name = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), default="BookOpen")

class TrainingCentre(Base):
    __tablename__ = "training_centres"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(24), unique=True, index=True, nullable=False) # CTR-0001
    name = Column(String(180), unique=True, nullable=False)
    location = Column(String(180), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), default="Karnataka")
    address = Column(Text, nullable=False)
    contact_phone = Column(String(30), nullable=True)
    contact_email = Column(String(180), nullable=True)
    delivery_modes = Column(String(120), default="Online, Hybrid, Classroom")
    facilities = Column(Text, default="High-speed internet, Advanced Computer Lab, Smart Classroom, Library")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    active = Column(Boolean, default=True)

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(24), unique=True, index=True, nullable=False) # TRN-0001
    name = Column(String(180), nullable=False)
    qualification = Column(String(180), nullable=False)
    specialisation = Column(String(180), nullable=False)
    experience_years = Column(Integer, default=5)
    contact_email = Column(String(180), nullable=True)
    assigned_centre_id = Column(Integer, ForeignKey("training_centres.id"), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    availability = Column(String(80), default="Available")
    active = Column(Boolean, default=True)

    centre = relationship("TrainingCentre", backref="trainers")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(24), unique=True, index=True, nullable=False) # SKL-0001
    name = Column(String(180), unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category_name = Column(String(120), index=True, nullable=False)
    level = Column(String(40), default="Beginner", index=True) # Beginner, Intermediate, Advanced
    duration_weeks = Column(Integer, default=6)
    duration_hours = Column(Integer, default=40)
    summary = Column(Text, default="")
    details = Column(Text, default="")
    prerequisites = Column(Text, default="Basic computer literacy")
    learning_objectives = Column(Text, default="")
    learning_outcomes = Column(Text, default="")
    relevant_industries = Column(String(255), default="Information Technology, Services")
    career_opportunities = Column(Text, default="")
    cert_info = Column(Text, default="Government of India Skill Qualification Framework (NSQF) aligned certificate")
    rating = Column(Float, default=4.8)
    enrolled_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    category = relationship("Category", backref="skills")
    modules = relationship("SkillModule", backref="skill", cascade="all, delete-orphan")

class SkillModule(Base):
    __tablename__ = "skill_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    module_order = Column(Integer, default=1)
    title = Column(String(180), nullable=False)
    description = Column(Text, default="")
    topics = Column(Text, default="") # JSON list or newline-separated
    practical_assignments = Column(Text, default="")
    projects = Column(Text, default="")

class TrainingProgram(Base):
    __tablename__ = "training_programs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(24), unique=True, index=True, nullable=False) # PRG-0001
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    title = Column(String(180), nullable=False)
    description = Column(Text, default="")
    provider_name = Column(String(180), default="NagrikSetu National Skill Academy")
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), nullable=True)
    mode = Column(String(40), default="Hybrid") # Online, Classroom, Hybrid
    duration_hours = Column(Integer, default=60)
    fee = Column(Float, default=0.0) # 0 for government funded
    scholarship_available = Column(Boolean, default=True)
    eligibility_criteria = Column(Text, default="10th Pass or 12th Pass / Diploma / Degree")
    start_date = Column(String(40), nullable=True)
    end_date = Column(String(40), nullable=True)
    status = Column(String(40), default="PUBLISHED") # PUBLISHED, ARCHIVED, UPCOMING
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    skill = relationship("Skill", backref="programs")
    trainer = relationship("Trainer", backref="programs")
    centre = relationship("TrainingCentre", backref="programs")
    batches = relationship("Batch", backref="program", cascade="all, delete-orphan")

    @property
    def delivery_mode(self):
        return self.mode

    @delivery_mode.setter
    def delivery_mode(self, val):
        self.mode = val

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(24), unique=True, index=True, nullable=False) # BAT-0001
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=False)
    batch_name = Column(String(180), nullable=False)
    timings = Column(String(120), default="Morning 09:00 AM - 11:30 AM")
    training_schedule = Column(String(120), default="Monday to Friday")
    mode = Column(String(40), default="Online") # Online, Offline, Hybrid
    total_seats = Column(Integer, default=30)
    available_seats = Column(Integer, default=30)
    start_date = Column(String(40), default="2026-11-20")
    end_date = Column(String(40), default="2026-12-31")
    application_deadline = Column(String(40), default="2026-11-18")
    status = Column(String(40), default="ADMISSIONS_OPEN") # ADMISSIONS_OPEN, FULL, IN_PROGRESS, COMPLETED

class CitizenProfile(Base):
    __tablename__ = "citizen_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_ref = Column(String(80), unique=True, index=True, nullable=False)
    full_name = Column(String(180), nullable=False)
    email = Column(String(180), nullable=False)
    phone = Column(String(30), nullable=True)
    education_qualification = Column(String(180), default="Bachelor of Engineering / Science")
    current_employment_status = Column(String(80), default="Job Seeker")
    work_experience_years = Column(Integer, default=0)
    interests = Column(Text, default="Software Engineering, AI, Cloud Computing")
    career_goals = Column(Text, default="Looking for technical roles in technology hubs")
    preferred_training_mode = Column(String(40), default="Hybrid")
    preferred_training_location = Column(String(100), default="Bengaluru")
    resume_summary = Column(Text, default="")
    date_of_birth = Column(String(30), nullable=True)
    gender = Column(String(20), nullable=True)
    residential_address = Column(Text, nullable=True)
    profile_completion_percentage = Column(Integer, default=85)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CitizenSkill(Base):
    __tablename__ = "citizen_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    skill_name = Column(String(120), nullable=False)
    proficiency = Column(String(40), default="Intermediate") # Beginner, Intermediate, Advanced

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(28), unique=True, index=True, nullable=False) # ENR-000001
    citizen_ref = Column(String(80), index=True, nullable=False)
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    skill_name = Column(String(180), nullable=False)
    program_title = Column(String(180), nullable=False)
    citizen_name = Column(String(180), nullable=False)
    citizen_email = Column(String(180), nullable=False)
    citizen_phone = Column(String(30), nullable=True)
    selected_mode = Column(String(40), default="Online")
    applicant_statement = Column(Text, default="")
    application_details = Column(Text, nullable=True) # Full 8-section government enrolment dossier JSON
    status = Column(String(40), default="PENDING", index=True) # PENDING, UNDER_REVIEW, ADDITIONAL_INFORMATION_REQUIRED, APPROVED, REJECTED, ENROLLED, IN_PROGRESS, COMPLETED, CANCELLED
    admin_remarks = Column(Text, default="")
    training_progress_pct = Column(Integer, default=0)
    attendance_pct = Column(Integer, default=0)
    assessment_score = Column(Integer, default=0)
    certificate_issued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    program = relationship("TrainingProgram", backref="enrollments")
    batch = relationship("Batch", backref="enrollments")
    history = relationship("EnrollmentStatusHistory", backref="enrollment", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", backref="enrollment", cascade="all, delete-orphan")
    module_progress_records = relationship("ModuleProgress", backref="enrollment", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", backref="enrollment", cascade="all, delete-orphan")

class EnrollmentStatusHistory(Base):
    __tablename__ = "enrollment_status_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    old_status = Column(String(40), nullable=True)
    new_status = Column(String(40), nullable=False)
    actor = Column(String(180), nullable=False)
    remarks = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False, index=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    session_date = Column(Date, nullable=False)
    session_topic = Column(String(180), default="Training Session")
    status = Column(String(20), nullable=False) # PRESENT, ABSENT, EXCUSED
    recorded_by = Column(String(180), nullable=False)
    remarks = Column(String(255), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('enrollment_id', 'session_date', name='uq_enrollment_session_date'),
    )

class ModuleProgress(Base):
    __tablename__ = "module_progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("skill_modules.id"), nullable=False, index=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    recorded_by = Column(String(180), nullable=True)
    remarks = Column(String(255), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    module = relationship("SkillModule")

    __table_args__ = (
        UniqueConstraint('enrollment_id', 'module_id', name='uq_enrollment_module'),
    )

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False, index=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    assessment_title = Column(String(180), nullable=False) # e.g. "Final Comprehensive Competency Assessment"
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, default=100.0, nullable=False)
    score_pct = Column(Float, nullable=False)
    assessment_date = Column(Date, nullable=False)
    evaluated_by = Column(String(180), nullable=False)
    remarks = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(40), unique=True, index=True, nullable=False) # CRT-000001
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), unique=True, nullable=False)
    citizen_ref = Column(String(80), index=True, nullable=False)
    citizen_name = Column(String(180), nullable=False)
    program_title = Column(String(180), nullable=False)
    skill_name = Column(String(180), nullable=False)
    grade = Column(String(40), default="Distinction (A+)")
    score_pct = Column(Integer, default=92)
    attendance_pct = Column(Integer, default=85)
    training_progress_pct = Column(Integer, default=100)
    issued_date = Column(String(40), nullable=False)
    verification_url = Column(String(255), nullable=True)
    issued_by = Column(String(180), default="Skill Department Administrator")

class SavedJob(Base):
    __tablename__ = "saved_jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    job_id = Column(String(64), nullable=False)
    title = Column(String(180), nullable=False)
    company = Column(String(180), nullable=False)
    location = Column(String(180), nullable=False)
    saved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class JobApplication(Base):
    __tablename__ = "job_applications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_ref = Column(String(64), unique=True, index=True, nullable=False)
    citizen_ref = Column(String(80), index=True, nullable=False)
    job_id = Column(String(64), nullable=False)
    job_title = Column(String(180), nullable=False)
    company = Column(String(180), nullable=False)
    location = Column(String(180), nullable=False)
    full_name = Column(String(180), nullable=False)
    email = Column(String(180), nullable=False)
    phone = Column(String(40), nullable=False)
    education = Column(String(180), nullable=True)
    experience_years = Column(String(40), nullable=True)
    statement = Column(Text, nullable=True)
    status = Column(String(50), default="SUBMITTED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    actor = Column(String(180), nullable=False)
    role = Column(String(40), default="CITIZEN")
    action = Column(String(100), nullable=False)
    target = Column(String(100), nullable=False)
    details = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CitizenDocument(Base):
    __tablename__ = "citizen_documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    doc_type = Column(String(60), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CitizenNotification(Base):
    __tablename__ = "citizen_notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_ref = Column(String(80), index=True, nullable=False)
    title = Column(String(180), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="GENERAL")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class OTPVerificationSession(Base):
    __tablename__ = "otp_verification_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reference = Column(String(80), unique=True, index=True, nullable=False)
    phone = Column(String(120), index=True, nullable=False)
    citizen_ref = Column(String(80), index=True, nullable=True)
    purpose = Column(String(60), nullable=False) # REGISTRATION, ENROLMENT, PROFILE_PHONE_UPDATE
    provider = Column(String(40), default="OTP.dev")
    provider_message_id = Column(String(120), nullable=True)
    hashed_code = Column(String(128), nullable=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    is_verified = Column(Boolean, default=False)
    is_consumed = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

