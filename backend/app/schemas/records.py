from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MedicalRecordResponse(BaseModel):
    id: int
    citizen_id: int
    blood_group: Optional[str] = "Unknown"
    chronic_conditions: Optional[str] = "None Reported"
    allergies: Optional[str] = "None"
    vaccination_status: Optional[str] = "Up to date"
    disability_status: Optional[str] = "None"
    abha_id: Optional[str] = None
    emergency_hospital: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalRecordUpdateRequest(BaseModel):
    blood_group: Optional[str] = None
    chronic_conditions: Optional[str] = None
    allergies: Optional[str] = None
    vaccination_status: Optional[str] = None
    disability_status: Optional[str] = None
    abha_id: Optional[str] = None
    emergency_hospital: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    otp_reference_id: Optional[str] = None


class EducationRecordResponse(BaseModel):
    id: int
    citizen_id: int
    highest_qualification: Optional[str] = None
    institution_name: Optional[str] = None
    specialization: Optional[str] = None
    year_of_completion: Optional[int] = None
    literacy_status: Optional[str] = None
    certificate_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EducationRecordUpdateRequest(BaseModel):
    highest_qualification: Optional[str] = None
    institution_name: Optional[str] = None
    specialization: Optional[str] = None
    year_of_completion: Optional[int] = None
    literacy_status: Optional[str] = None
    certificate_number: Optional[str] = None
    otp_reference_id: Optional[str] = None


class LandRecordResponse(BaseModel):
    id: int
    household_id: int
    survey_number: str
    land_type: str
    area_measurement: str
    patta_passbook_number: Optional[str] = None
    district_sub_registrar: Optional[str] = None
    property_tax_status: Optional[str] = None
    market_valuation_inr: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LandRecordCreateRequest(BaseModel):
    survey_number: str
    land_type: str = "Agricultural"
    area_measurement: str
    patta_passbook_number: Optional[str] = None
    district_sub_registrar: Optional[str] = None
    property_tax_status: Optional[str] = "Paid"
    market_valuation_inr: Optional[float] = None


class HouseholdDossierResponse(BaseModel):
    household_id: int
    household_code: str
    address_line: str
    locality: str
    city: str
    state: str
    postal_code: str
    members_count: int
    land_records: list[LandRecordResponse]
    family_members: list[dict]
