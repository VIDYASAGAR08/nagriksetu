from datetime import datetime, timezone
import uuid
import json
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class OutboxEvent(Base):
    """
    Outbox table capturing committed domain events for administrative services.
    Enables future API Gateway and microservices integration (FR-ADM-025).
    """
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(String(50), unique=True, index=True, default=lambda: f"EVT-{uuid.uuid4().hex[:12].upper()}")
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False, index=True)
    aggregate_id = Column(String(100), nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    @classmethod
    def create(cls, event_type: str, aggregate_type: str, aggregate_id: str, payload: dict):
        return cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload_json=json.dumps(payload, default=str),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "payload": json.loads(self.payload_json) if self.payload_json else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<OutboxEvent {self.event_id} type={self.event_type}>"
