from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        actor: str,
        action: str,
        entity_type: str,
        actor_role: str = "OFFICER",
        entity_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: str = "127.0.0.1"
    ) -> AuditLog:
        audit = AuditLog(
            actor=actor,
            actor_role=actor_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def get_logs(db: Session, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
