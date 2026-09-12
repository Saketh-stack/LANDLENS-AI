from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from backend.app.core.database import Base

class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(100), unique=True, index=True, nullable=False)
    source = Column(String(100), default='Sub-Registrar Office (Mock API)')
    owner_name = Column(String(200), nullable=False)
    father_husband_name = Column(String(200), nullable=True)
    survey_number = Column(String(100), nullable=False)
    khasra_number = Column(String(100), nullable=True)
    khata_number = Column(String(100), nullable=True)
    village = Column(String(100), nullable=False)
    tehsil = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), default='Madhya Pradesh')
    land_area = Column(Float, nullable=False)
    land_classification = Column(String(100), default='Agricultural')
    registration_date = Column(String(50), nullable=False)
    expected_public_date = Column(String(50), nullable=False)

    document_name = Column(String(255), nullable=True)
    status = Column(String(50), default='RECEIVED')
    confidence_score = Column(Float, default=92.0)
    has_mismatch = Column(Boolean, default=False)
    mismatch_details = Column(Text, nullable=True)

    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
