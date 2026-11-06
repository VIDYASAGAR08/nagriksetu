from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class MedicalRecord(Base):
    """
    Confidential health & medical profile of household citizens.
    Protected under privacy controls (FR-ADM-007 & FR-ADM-008).
    """
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    citizen_id = Column(Integer, ForeignKey("citizen_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    blood_group = Column(String(10), nullable=True, default="Unknown")
    chronic_conditions = Column(String(255), nullable=True, default="None Reported")
    allergies = Column(String(255), nullable=True, default="None")
    vaccination_status = Column(String(100), nullable=True, default="Up to date")
    disability_status = Column(String(100), nullable=True, default="None")
    abha_id = Column(String(50), nullable=True)  # Ayushman Bharat Health Account ID
    emergency_hospital = Column(String(200), nullable=True)
    emergency_contact_name = Column(String(150), nullable=True)
    emergency_contact_phone = Column(String(30), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationship
    citizen = relationship("CitizenProfile", back_populates="medical_record")

    def __repr__(self):
        return f"<MedicalRecord citizen_id={self.citizen_id} blood_group={self.blood_group}>"


class EducationRecord(Base):
    """
    Academic qualifications, literacy status, and institutional records of citizens.
    """
    __tablename__ = "education_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    citizen_id = Column(Integer, ForeignKey("citizen_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    highest_qualification = Column(String(150), nullable=True, default="Secondary (10th)")
    institution_name = Column(String(255), nullable=True)
    specialization = Column(String(150), nullable=True)
    year_of_completion = Column(Integer, nullable=True)
    literacy_status = Column(String(100), nullable=True, default="Literate")
    certificate_number = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationship
    citizen = relationship("CitizenProfile", back_populates="education_record")

    def __repr__(self):
        return f"<EducationRecord citizen_id={self.citizen_id} qualification={self.highest_qualification}>"


class LandRecord(Base):
    """
    Land parcel, survey, and immovable property assets linked to a household dwelling.
    """
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True)

    survey_number = Column(String(100), nullable=False)  # Khasra / Survey Number
    land_type = Column(String(100), nullable=False, default="Agricultural")  # Agricultural, Residential, Commercial
    area_measurement = Column(String(100), nullable=False)  # e.g., '2.5 Acres' or '1,500 sq.ft'
    patta_passbook_number = Column(String(100), nullable=True)
    district_sub_registrar = Column(String(150), nullable=True)
    property_tax_status = Column(String(50), nullable=True, default="Paid")
    market_valuation_inr = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationship
    household = relationship("Household", back_populates="land_records")

    def __repr__(self):
        return f"<LandRecord survey={self.survey_number} type={self.land_type} household_id={self.household_id}>"
