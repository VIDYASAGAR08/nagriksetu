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
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    account_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthMeResponse(BaseModel):
    user: UserResponse
    citizen_profile: Optional[dict] = None
