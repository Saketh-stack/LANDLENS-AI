from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.app.core.database import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(100), nullable=False)
    actor_role = Column(String(50), default='OFFICER')
    action = Column(String(150), nullable=False)
    entity_type = Column(String(50), nullable=False)  # LAND_RECORD, REGISTRATION, DOCUMENT, SYSTEM
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), default='127.0.0.1')
    timestamp = Column(DateTime, default=datetime.utcnow)
