import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(30), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CITIZEN.value, nullable=False)
    account_status = Column(String(50), default=UserStatus.ACTIVE.value, nullable=False)
    # Administrative Scope assignment (FR-ADM-021)
    # If null, admin has national / unrestricted scope.
    administrative_unit_id = Column(Integer, ForeignKey("administrative_units.id", ondelete="SET NULL"), nullable=True, index=True)
    # WebAuthn / Biometric (Fingerprint & FaceID) fields
    biometric_credential_id = Column(String(255), nullable=True, unique=True, index=True)
    biometric_public_key = Column(String(512), nullable=True)
    biometric_registered_at = Column(DateTime(timezone=True), nullable=True)
    face_data = Column(Text, nullable=True)  # Biometric facial template / Base64 snapshot
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    @property
    def biometric_enabled(self) -> bool:
        return self.biometric_credential_id is not None

    @property
    def has_face_enrolled(self) -> bool:
        return self.face_data is not None

    # Relationships
    citizen_profile = relationship("CitizenProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor", foreign_keys="AuditLog.actor_id")
    administrative_unit = relationship("AdministrativeUnit", back_populates="scoped_admins")

    __table_args__ = (
        CheckConstraint("role IN ('citizen', 'admin')", name="check_valid_user_role"),
        CheckConstraint("account_status IN ('active', 'suspended', 'pending')", name="check_valid_user_status"),
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
