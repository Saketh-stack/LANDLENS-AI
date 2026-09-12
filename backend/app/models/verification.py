from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class VerificationRecord(Base):
    __tablename__ = 'verification_records'

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)
    officer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    officer_name = Column(String(150), nullable=False)
    action = Column(String(50), nullable=False)  # APPROVED, REJECTED, SENT_BACK, CORRECTION_SAVED
    remarks = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    land_record = relationship('LandRecord', back_populates='verification_records')
