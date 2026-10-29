import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class AdministrativeUnitType(str, enum.Enum):
    COUNTRY = "country"
    STATE = "state"
    DISTRICT = "district"
    SUB_DISTRICT = "sub_district"
    WARD = "ward"
    VILLAGE = "village"


class AdministrativeUnitStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AdministrativeUnit(Base):
    __tablename__ = "administrative_units"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    identifier = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False, index=True)
    unit_type = Column(String(50), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("administrative_units.id", ondelete="RESTRICT"), nullable=True, index=True)
    status = Column(String(50), default=AdministrativeUnitStatus.ACTIVE.value, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Self-referential hierarchy relationship
    parent = relationship("AdministrativeUnit", remote_side=[id], back_populates="children")
    children = relationship("AdministrativeUnit", back_populates="parent", cascade="all")

    # Mapped entities within this administrative boundary
    citizens = relationship("CitizenProfile", back_populates="administrative_unit")
    households = relationship("Household", back_populates="administrative_unit")
    scoped_admins = relationship("User", back_populates="administrative_unit")

    __table_args__ = (
        CheckConstraint(
            "unit_type IN ('country', 'state', 'district', 'sub_district', 'ward', 'village')",
            name="check_valid_unit_type"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name="check_valid_unit_status"
        ),
    )

    def __repr__(self):
        return f"<AdministrativeUnit id={self.id} code={self.identifier} name={self.name} type={self.unit_type}>"
