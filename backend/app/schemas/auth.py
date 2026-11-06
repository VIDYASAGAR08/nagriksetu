from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class CitizenRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, description="Full legal name of the citizen")
    email: EmailStr = Field(..., description="Unique email address used for signing in")
    password: str = Field(..., min_length=8, description="Secure account password")
    confirm_password: str = Field(..., description="Confirmation of password")
    preferred_language: str = Field(default="en", max_length=10, description="Preferred interface language code")
    phone_number: Optional[str] = Field(None, max_length=30, description="Optional phone number")
    date_of_birth: Optional[str] = None
    face_data: Optional[str] = Field(None, description="Captured base64 facial biometric snapshot/descriptor at registration")
    biometric_credential_id: Optional[str] = Field(None, description="Enrolled Touch ID / FIDO2 Passkey credential")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return cleaned


class LoginRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    password: str


class LoginOTPRequest(BaseModel):
    identifier: str = Field(..., min_length=3, description="Email or registered phone number")


class LoginOTPVerifyRequest(BaseModel):
    identifier: str = Field(..., min_length=3, description="Email or registered phone number")
    reference_id: str = Field(..., description="OTP Reference ID")
    otp_code: str = Field(..., min_length=4, max_length=8, description="6-digit verification code")


class BiometricLoginRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    credential_id: Optional[str] = None
    biometric_type: str = Field(default="face", description="face, fingerprint, or webauthn")
    face_data: Optional[str] = None
    client_data_hash: Optional[str] = None
    require_otp: bool = Field(default=False, description="When true, triggers 2FA OTP verification step upon biometric match")


class BiometricRegisterRequest(BaseModel):
    credential_id: str
    public_key: Optional[str] = None
    biometric_type: str = "webauthn"


class OTPRequest(BaseModel):
    purpose: str = Field(default="CITIZEN_PROFILE_UPDATE", description="Purpose of verification challenge")
    recipient: Optional[str] = Field(None, description="Optional phone or email; defaults to user's registered contact")


class OTPVerifyRequest(BaseModel):
    reference_id: str
    otp_code: str
    purpose: str = "CITIZEN_PROFILE_UPDATE"


class OTPResponse(BaseModel):
    reference_id: str
    recipient: str
    purpose: str
    expires_in_seconds: int = 300
    demo_hint: Optional[str] = None  # Presented in demo mode for instant evaluator testing
    message: str


class OTPVerifyResponse(BaseModel):
    success: bool
    reference_id: str
    verified: bool
    message: str


class UserResponse(BaseModel):
    id: int
    email: str
    phone_number: Optional[str] = None
    role: str
    account_status: str
    biometric_enabled: bool = False
    has_face_enrolled: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str = Field(default="", description="JWT access token")
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
    match_score: Optional[float] = None
    message: Optional[str] = None
    requires_otp: bool = False
    reference_id: Optional[str] = None
    recipient: Optional[str] = None
    demo_hint: Optional[str] = None
    identifier: Optional[str] = None


class AuthMeResponse(BaseModel):
    user: UserResponse
    citizen_profile: Optional[dict] = None
