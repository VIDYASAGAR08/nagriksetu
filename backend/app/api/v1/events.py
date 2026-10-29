from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.event import OutboxEvent
from app.schemas.event import OutboxEventListResponse, OutboxEventResponse

router = APIRouter(prefix="/integrations", tags=["Service Integration & Domain Events"])


@router.get("/events", response_model=OutboxEventListResponse)
def list_domain_events(
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. CITIZEN_REGISTERED, HIERARCHY_UNIT_CREATED)"),
    aggregate_type: Optional[str] = Query(None, description="Filter by aggregate type (citizen, household, hierarchy, scope)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    FR-ADM-025: Service integration API exposing committed domain events
    for downstream microservices, notifications, and API Gateway integration.
    """
    query = db.query(OutboxEvent)

    if event_type:
        query = query.filter(OutboxEvent.event_type == event_type.strip())

    if aggregate_type:
        query = query.filter(OutboxEvent.aggregate_type == aggregate_type.strip().lower())

    total = query.count()
    events = query.order_by(OutboxEvent.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [OutboxEventResponse(**e.to_dict()) for e in events]
    return OutboxEventListResponse(total=total, page=page, page_size=page_size, items=items)
