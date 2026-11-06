from datetime import datetime, date
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
    household_role: Optional[str] = "MEMBER"
    assigned_tasks: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class HouseholdBase(BaseModel):
    address_line: str = Field(..., min_length=3, max_length=255)
    locality: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    administrative_unit_id: Optional[int] = None


class HouseholdResponse(HouseholdBase):
    id: int
    household_code: str
    administrative_unit_name: Optional[str] = None
    members: List[HouseholdMemberSummary] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminHouseholdResponse(HouseholdResponse):
    administrative_notes: Optional[str] = None
    consistency_flags: List[str] = []  # FR-ADM-019
    duplicate_warning: bool = False   # FR-ADM-020
    matching_households: List[str] = []


class AdminHouseholdCreateRequest(HouseholdBase):
    household_code: Optional[str] = None
    administrative_notes: Optional[str] = None


class AdminHouseholdUpdateRequest(BaseModel):
    address_line: Optional[str] = None
    locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    administrative_unit_id: Optional[int] = None
    administrative_notes: Optional[str] = None


class HouseholdMemberAssignRequest(BaseModel):
    citizen_id: int
    household_relationship: Optional[str] = Field(default="Member", max_length=100)


class HouseholdMembershipResponse(BaseModel):
    id: int
    household_id: int
    citizen_id: int
    citizen_code: str
    citizen_name: str
    relationship_type: str
    start_date: date
    end_date: Optional[date] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HouseholdMembershipEndRequest(BaseModel):
    end_date: Optional[date] = None
    notes: Optional[str] = None


class HouseholdLinkSubmitRequest(BaseModel):
    """
    Citizen request to link a new family member to their registered household.
    - Relationship is explicitly chosen by the user (NOT auto-assigned by system or admin).
    - Role and task permissions are explicitly defined by the user.
    """
    target_citizen_code: str = Field(..., description="Target citizen's unique code or phone number")
    relationship: str = Field(..., min_length=2, max_length=100, description="User-specified family relationship")
    household_role: str = Field(default="MEMBER", description="HEAD, DEPUTY, MEMBER, DEPENDENT")
    assigned_tasks: List[str] = Field(default=[], description="Explicit tasks assigned to this member")


class HouseholdLinkActionRequest(BaseModel):
    """
    Admin approval action.
    Crucial Rule: Admin CANNOT modify or assign roles or relationships. Admin ONLY accepts or rejects.
    """
    action: str = Field(..., pattern="^(approve|reject)$", description="'approve' or 'reject'")
    admin_notes: Optional[str] = Field(None, max_length=255, description="Administrative audit note or reason")


class HouseholdLinkRequestResponse(BaseModel):
    id: int
    household_id: int
    household_code: str
    requester_citizen_id: int
    requester_name: str
    target_citizen_id: int
    target_citizen_code: str
    target_citizen_name: str
    relationship: str
    household_role: str
    assigned_tasks: List[str]
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
