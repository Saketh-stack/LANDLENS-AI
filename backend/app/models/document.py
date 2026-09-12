from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)

    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # PDF, JPG, PNG
    file_size = Column(Integer, nullable=True)  # in bytes
    file_hash = Column(String(100), index=True, nullable=True)  # SHA-256
    document_type = Column(String(100), default='Sale Deed')
    language = Column(String(50), default='English')
    ocr_status = Column(String(50), default='COMPLETED')  # PENDING, PROCESSING, COMPLETED, FAILED
    ocr_raw_text = Column(Text, nullable=True)
    processing_status = Column(String(50), default='SUCCESS')
    uploaded_by = Column(String(100), default='Officer')

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    land_record = relationship('LandRecord', back_populates='documents')
