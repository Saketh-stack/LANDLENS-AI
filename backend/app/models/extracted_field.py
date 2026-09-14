from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ExtractedField(Base):
    __tablename__ = 'extracted_fields'

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)

    field_name = Column(String(100), nullable=False)
    field_label = Column(String(100), nullable=False)
    extracted_value = Column(String(255), nullable=True)
    corrected_value = Column(String(255), nullable=True)
    source_text = Column(Text, nullable=True)
    confidence = Column(Float, default=95.0)
    confidence_tier = Column(String(20), default='HIGH')
    requires_review = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    page_number = Column(Integer, default=1)
    ocr_confidence = Column(Float, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # {"x": int, "y": int, "w": int, "h": int}

    land_record = relationship('LandRecord', back_populates='extracted_fields')
