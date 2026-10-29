from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.citizen import CitizenProfileResponse


class AdminDashboardMetrics(BaseModel):
    total_citizens: int
    active_citizens: int
    pending_citizens: int
    total_households: int
    total_administrative_units: int = 0
    active_units: int = 0
    admin_scope: str = "National (All Areas)"
    admin_scope_unit_id: Optional[int] = None
    recent_registrations: List[CitizenProfileResponse] = []


class AdminScopeAssignRequest(BaseModel):
    user_id: int
    administrative_unit_id: Optional[int] = None


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
