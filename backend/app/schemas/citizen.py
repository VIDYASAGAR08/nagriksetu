from datetime import date, datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator


class CitizenProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=30)
    preferred_language: str = Field(default="en", max_length=10)

    @field_validator("phone_number", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> Optional[str]:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class CitizenProfileResponse(CitizenProfileBase):
    id: int
    citizen_code: str
    date_of_birth: Optional[date] = None
    profile_status: str
    household_id: Optional[int] = None
    household_relationship: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CitizenProfileUpdateRequest(BaseModel):
    """
    Fields that a citizen is permitted to update on their own profile.
    Notice: role, account_status, citizen_code, profile_status, and household assignment
    CANNOT be changed by the citizen.
    """
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=30)
    preferred_language: Optional[str] = Field(None, max_length=10)
    date_of_birth: Optional[date] = None

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def clean_dob(cls, v: Any) -> Optional[date]:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("phone_number", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> Optional[str]:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class AdminCitizenCreateRequest(CitizenProfileBase):
    email: Optional[EmailStr] = None
    initial_password: Optional[str] = None
    date_of_birth: Optional[date] = None
    profile_status: str = Field(default="pending_review")
    household_id: Optional[int] = None
    household_relationship: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: Any) -> Optional[str]:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def clean_dob(cls, v: Any) -> Optional[date]:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class AdminCitizenUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=30)
    date_of_birth: Optional[date] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    profile_status: Optional[str] = None
    household_id: Optional[int] = None
    household_relationship: Optional[str] = None

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def clean_dob(cls, v: Any) -> Optional[date]:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("phone_number", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> Optional[str]:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class AdminStatusUpdateRequest(BaseModel):
    profile_status: str = Field(..., description="Target profile status: 'pending_review', 'active', or 'archived'")
