from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class OutboxEventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: Dict[str, Any]
    created_at: Optional[str] = None


class OutboxEventListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[OutboxEventResponse]
