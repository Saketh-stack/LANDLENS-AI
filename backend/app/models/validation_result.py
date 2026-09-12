from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ValidationResult(Base):
    __tablename__ = 'validation_results'

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)

    rule_id = Column(String(100), nullable=False)
    rule_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False)  # PASS, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    land_record = relationship('LandRecord', back_populates='validation_results')
