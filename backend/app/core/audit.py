import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.user import User


def record_audit_log(
    db: Session,
    actor: User,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Safely record an administrative audit event.
    Sanitizes details so passwords, hashes, or tokens are never logged.
    """
    safe_details = {}
    if details:
        for k, v in details.items():
            if any(secret_key in k.lower() for secret_key in ["password", "token", "secret", "hash", "key"]):
                continue
            safe_details[k] = v

    log_entry = AuditLog(
        actor_id=actor.id if actor else None,
        actor_email=actor.email if actor else "system",
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=json.dumps(safe_details) if safe_details else None,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
