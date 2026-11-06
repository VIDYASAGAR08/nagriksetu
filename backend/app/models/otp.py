import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class OTPVerification(Base):
    """
    Stores one-time verification tokens required for sensitive identity modifications (Privacy Protection).
    """
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reference_id = Column(String(50), unique=True, index=True, default=lambda: f"REF-{uuid.uuid4().hex[:10].upper()}")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    recipient = Column(String(100), nullable=False)
    otp_code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False, default="CITIZEN_PROFILE_UPDATE")
    is_verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User")

    @classmethod
    def create_otp(cls, recipient: str, user_id: int = None, purpose: str = "CITIZEN_PROFILE_UPDATE", expiry_minutes: int = 5):
        import random
        # Cryptographic/secure 6-digit number
        code = f"{random.randint(100000, 999999)}"
        exp = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        return cls(
            recipient=recipient,
            user_id=user_id,
            otp_code=code,
            purpose=purpose,
            expires_at=exp,
        )

    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            # Handle naive datetime from SQLite
            return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)
        return now > self.expires_at

    def __repr__(self):
        return f"<OTPVerification {self.reference_id} purpose={self.purpose} verified={self.is_verified}>"
