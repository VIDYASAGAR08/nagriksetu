from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


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
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    members = relationship("CitizenProfile", back_populates="household")

    def __repr__(self):
        return f"<Household id={self.id} code={self.household_code} city={self.city}>"
