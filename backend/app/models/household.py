import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"


class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_code = Column(String(50), unique=True, index=True, nullable=False)
    address_line = Column(String(255), nullable=False)
    locality = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    administrative_notes = Column(Text, nullable=True)

    # Administrative Unit / Area Mapping (FR-ADM-021)
    administrative_unit_id = Column(Integer, ForeignKey("administrative_units.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    members = relationship("CitizenProfile", back_populates="household")
    administrative_unit = relationship("AdministrativeUnit", back_populates="households")
    membership_records = relationship("HouseholdMembership", back_populates="household", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Household id={self.id} code={self.household_code} city={self.city}>"


class HouseholdMembership(Base):
    """
    Historical log and explicit tracking of citizen-to-household memberships (FR-ADM-016).
    Retains history when memberships are updated or ended.
    """
    __tablename__ = "household_memberships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True)
    citizen_id = Column(Integer, ForeignKey("citizen_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(100), nullable=False)
    start_date = Column(Date, default=date.today, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(50), default=MembershipStatus.ACTIVE.value, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    household = relationship("Household", back_populates="membership_records")
    citizen = relationship("CitizenProfile")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'ended')", name="check_valid_membership_status"),
    )

    def __repr__(self):
        return f"<HouseholdMembership citizen_id={self.citizen_id} household_id={self.household_id} role={self.relationship_type} status={self.status}>"
