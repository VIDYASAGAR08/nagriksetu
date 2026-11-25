from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

class CentreInfoBrief(BaseModel):
    id: int
    code: str
    name: str
    district: str
    location: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    citizen_ref: Optional[str] = None
    centre_id: Optional[int] = None
    email: str
    full_name: Optional[str] = None
    assigned_centres: Optional[List[CentreInfoBrief]] = None
    is_student: Optional[bool] = False
    student_id: Optional[str] = None

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5)
    password: Optional[str] = None
    full_name: str = Field(min_length=2)
    phone: Optional[str] = None
    citizen_ref: Optional[str] = None
    otp_reference: Optional[str] = None

class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: Optional[str] = None
    otp_reference: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    education_qualification: Optional[str] = None
    current_employment_status: Optional[str] = None
    work_experience_years: Optional[int] = None
    interests: Optional[str] = None
    career_goals: Optional[str] = None
    preferred_training_mode: Optional[str] = None
    preferred_training_location: Optional[str] = None
    resume_summary: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    residential_address: Optional[str] = None
    otp_reference: Optional[str] = None

class AddCitizenSkillRequest(BaseModel):
    skill_name: str
    proficiency: str = "Intermediate"

class EnrollmentCreateRequest(BaseModel):
    program_id: int
    batch_id: Optional[int] = None
    selected_mode: Optional[str] = "Online"
    applicant_statement: Optional[str] = ""
    application_details: Optional[dict] = None
    otp_reference: Optional[str] = None

class ApplicationReviewRequest(BaseModel):
    status: str
    remarks: str = Field(min_length=2)

class AttendanceRecordRequest(BaseModel):
    session_date: date
    session_topic: Optional[str] = "Training Lecture & Practical"
    status: str = "PRESENT" # PRESENT, ABSENT, EXCUSED
    remarks: Optional[str] = ""

class ModuleProgressUpdateRequest(BaseModel):
    module_id: int
    is_completed: bool
    remarks: Optional[str] = ""

class AssessmentRecordRequest(BaseModel):
    assessment_title: Optional[str] = "Comprehensive Competency Assessment"
    marks_obtained: float = Field(ge=0.0)
    max_marks: float = Field(default=100.0, gt=0.0)
    assessment_date: Optional[date] = None
    remarks: Optional[str] = ""

class ProgressUpdateRequest(BaseModel):
    training_progress_pct: int = Field(ge=0, le=100)
    attendance_pct: int = Field(ge=0, le=100)
    assessment_score: int = Field(ge=0, le=100)

class SkillCreateUpdateRequest(BaseModel):
    name: str = Field(min_length=3)
    category_id: Optional[int] = None
    category_name: str
    level: str = "Beginner"
    duration_weeks: int = 6
    duration_hours: int = 40
    summary: str = ""
    details: str = ""
    prerequisites: str = "Basic computer literacy"
    learning_objectives: str = ""
    learning_outcomes: str = ""
    relevant_industries: str = ""
    career_opportunities: str = ""

class ProgramCreateUpdateRequest(BaseModel):
    skill_id: int
    title: str
    description: str = ""
    trainer_id: Optional[int] = None
    centre_id: Optional[int] = None
    mode: str = "Hybrid"
    duration_hours: int = 40
    fee: float = 0.0
    scholarship_available: bool = True
    eligibility_criteria: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class BatchCreateUpdateRequest(BaseModel):
    program_id: int
    batch_name: str
    timings: str
    training_schedule: str
    mode: str = "Online"
    total_seats: int = 30
    start_date: str
    end_date: str
    application_deadline: str

class TrainerCreateUpdateRequest(BaseModel):
    name: str
    qualification: str
    specialisation: str
    experience_years: int
    contact_email: Optional[str] = None
    assigned_centre_id: Optional[int] = None
    availability: Optional[str] = "Available"

class CentreCreateUpdateRequest(BaseModel):
    name: str
    location: str
    district: str
    state: str = "Karnataka"
    address: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    delivery_modes: Optional[str] = "Online, Hybrid, Classroom"
    facilities: Optional[str] = "Computer Lab, Smart Classrooms, High-speed Internet"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SkillGapAnalysisRequest(BaseModel):
    target_role: str
    current_skills: Optional[List[str]] = None

class JobApplyRequest(BaseModel):
    job_id: str
    full_name: str
    email: str
    phone: str
    education: Optional[str] = None
    experience_years: Optional[str] = None
    statement: Optional[str] = None

class OTPSendRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    channel: Optional[str] = None # "email" or "sms"
    purpose: str = "REGISTRATION" # REGISTRATION, ENROLMENT, PROFILE_PHONE_UPDATE

class OTPVerifyRequest(BaseModel):
    reference: str
    code: str



class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3)
    otp_reference: str
    new_password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

class SetPasswordRequest(BaseModel):
    email: Optional[str] = None
    otp_reference: Optional[str] = None
    new_password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

class CreateCentreAdminRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2)
    phone: Optional[str] = None
    centre_id: Optional[int] = None

class CentreStatusUpdateRequest(BaseModel):
    approval_status: Optional[str] = None
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
    reason: Optional[str] = None

class CentreProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    delivery_modes: Optional[str] = None
    facilities: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    history: Optional[str] = None
    mission_objectives: Optional[str] = None
    achievements: Optional[str] = None
    certifications: Optional[str] = None
    establishment_year: Optional[int] = None
    classroom_count: Optional[int] = None
    lab_details: Optional[str] = None
    equipment_details: Optional[str] = None

class CentreAdminApplicationReviewRequest(BaseModel):
    action: str = Field(..., description="APPROVE, REJECT, UNDER_REVIEW, ACTION_REQUIRED, WAITLIST, or WITHDRAW")
    remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    internal_notes: Optional[str] = None

class CentreAdminEnrolApplicantRequest(BaseModel):
    batch_id: int
    internal_notes: Optional[str] = None



class CentreRegistrationRequest(BaseModel):
    centre_name: str = Field(..., min_length=3)
    location: str = Field(..., min_length=2)
    address: str = Field(..., min_length=5)
    district: Optional[str] = 'Karnataka'
    state: Optional[str] = 'Karnataka'
    representative_name: str = Field(..., min_length=2)
    representative_phone: str = Field(..., min_length=8)
    representative_email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
    delivery_modes: Optional[str] = 'Classroom, Lab Practical, Hybrid'
    facilities: Optional[str] = 'Computer Labs, Advanced Equipment'

class CentreRepresentativeRegisterRequest(BaseModel):
    centre_id: int
    representative_name: str = Field(min_length=2)
    representative_phone: str = Field(min_length=8)
    representative_email: str = Field(min_length=5)
    password: str = Field(min_length=6)

class ProjectOwnerLoginRequest(BaseModel):
    owner_key: str = Field(min_length=6)

class ProjectOwnerResetRequest(BaseModel):
    centre_id: int
    secret_key: Optional[str] = None
    new_password: str = Field(min_length=6)
