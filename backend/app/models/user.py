from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from backend.app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default='CITIZEN', nullable=False)  # CITIZEN, LAND_RECORD_OFFICER, REGISTRATION_OFFICER, ADMIN
    department = Column(String(100), default='Revenue Department')
    designation = Column(String(100), default='Revenue Officer')
    state_id = Column(Integer, ForeignKey('states.id'), nullable=True)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
