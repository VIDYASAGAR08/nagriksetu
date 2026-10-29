from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class HouseholdMemberSummary(BaseModel):
    """
    Safe summary of household members.
    Crucial privacy rule: Avoids leaking private phone numbers, emails, or user accounts of co-residents.
    """
    id: int
    citizen_code: str
    full_name: str
    household_relationship: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HouseholdBase(BaseModel):
    address_line: str = Field(..., min_length=3, max_length=255)
    locality: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)


class HouseholdResponse(HouseholdBase):
    id: int
    household_code: str
    members: List[HouseholdMemberSummary] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminHouseholdResponse(HouseholdResponse):
    administrative_notes: Optional[str] = None


class AdminHouseholdCreateRequest(HouseholdBase):
    household_code: Optional[str] = None
    administrative_notes: Optional[str] = None


class AdminHouseholdUpdateRequest(BaseModel):
    address_line: Optional[str] = None
    locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    administrative_notes: Optional[str] = None


class HouseholdMemberAssignRequest(BaseModel):
    citizen_id: int
    household_relationship: Optional[str] = Field(default="Member", max_length=100)
