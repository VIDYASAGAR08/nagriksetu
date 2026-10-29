from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.citizen import CitizenProfileResponse


class AdminDashboardMetrics(BaseModel):
    total_citizens: int
    active_citizens: int
    pending_citizens: int
    total_households: int
    recent_registrations: List[CitizenProfileResponse] = []


class AuditLogResponse(BaseModel):
    id: int
    actor_id: Optional[int] = None
    actor_email: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
