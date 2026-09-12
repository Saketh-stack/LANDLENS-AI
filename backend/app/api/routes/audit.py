from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["Audit & Telemetry"])

@router.get("/logs", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def get_audit_logs(limit: int = Query(100, le=500), db: Session = Depends(get_db)):
    logs = AuditService.get_logs(db, limit=limit)
    return [
        {
            "id": log.id,
            "actor": log.actor,
            "actor_role": log.actor_role,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.strftime("%d-%m-%Y %H:%M:%S") if log.timestamp else ""
        }
        for log in logs
    ]
