import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ProfileStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    ARCHIVED = "archived"


def utc_now():
    return datetime.now(timezone.utc)


class CitizenProfile(Base):
    __tablename__ = "citizen_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    citizen_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    phone_number = Column(String(30), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    profile_status = Column(String(50), default=ProfileStatus.PENDING_REVIEW.value, nullable=False)
    
    # Household association
    household_id = Column(Integer, ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True)
    household_relationship = Column(String(100), nullable=True)

    # Administrative Unit / Area Mapping (FR-ADM-021)
    administrative_unit_id = Column(Integer, ForeignKey("administrative_units.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="citizen_profile")
    household = relationship("Household", back_populates="members")
    administrative_unit = relationship("AdministrativeUnit", back_populates="citizens")

    __table_args__ = (
        CheckConstraint("profile_status IN ('pending_review', 'active', 'archived')", name="check_valid_profile_status"),
    )

    def __repr__(self):
        return f"<CitizenProfile id={self.id} code={self.citizen_code} name={self.full_name}>"
