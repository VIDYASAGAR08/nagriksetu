import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship as orm_relationship
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
    members = orm_relationship("CitizenProfile", back_populates="household")
    administrative_unit = orm_relationship("AdministrativeUnit", back_populates="households")
    membership_records = orm_relationship("HouseholdMembership", back_populates="household", cascade="all, delete-orphan")
    land_records = orm_relationship("LandRecord", back_populates="household", cascade="all, delete-orphan")

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
    household = orm_relationship("Household", back_populates="membership_records")
    citizen = orm_relationship("CitizenProfile")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'ended')", name="check_valid_membership_status"),
    )

    def __repr__(self):
        return f"<HouseholdMembership citizen_id={self.citizen_id} household_id={self.household_id} role={self.relationship_type} status={self.status}>"


class LinkRequestStatus(str, enum.Enum):
    PENDING = "pending_admin_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class HouseholdLinkRequest(Base):
    """
    FR-ADM-019 & Teacher Feedback:
    Citizen requests to link a family member to their household.
    - The relationship is explicitly specified by the citizen (NOT auto-decided or assigned by system or admin).
    - Roles and individual assigned tasks are specified by the citizen.
    - Admin strictly acts as an approval/activation gate (accept or reject only).
    - Admin CANNOT modify or assign roles/relationships.
    """
    __tablename__ = "household_link_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True)
    requester_citizen_id = Column(Integer, ForeignKey("citizen_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    target_citizen_id = Column(Integer, ForeignKey("citizen_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Specified by the user
    relationship = Column(String(100), nullable=False)
    household_role = Column(String(50), default="MEMBER", nullable=False)
    assigned_tasks = Column(Text, default="[]", nullable=False)  # JSON-encoded array of task codes

    status = Column(String(50), default=LinkRequestStatus.PENDING.value, nullable=False, index=True)
    admin_notes = Column(Text, nullable=True)
    reviewed_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    household = orm_relationship("Household")
    requester = orm_relationship("CitizenProfile", foreign_keys=[requester_citizen_id])
    target = orm_relationship("CitizenProfile", foreign_keys=[target_citizen_id])
    reviewed_by = orm_relationship("User", foreign_keys=[reviewed_by_admin_id])

    def __repr__(self):
        return f"<HouseholdLinkRequest id={self.id} household_id={self.household_id} target={self.target_citizen_id} status={self.status}>"
