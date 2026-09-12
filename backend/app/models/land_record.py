from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class LandRecord(Base):
    __tablename__ = 'land_records'

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey('states.id'), nullable=True)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=True)
    administrative_unit_id = Column(Integer, ForeignKey('administrative_units.id'), nullable=True)
    village_id = Column(Integer, ForeignKey('villages.id'), nullable=True)
    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=True)

    # Denormalized location & owner names for rapid lookup & backwards compatibility
    owner_name = Column(String(200), index=True, nullable=False)
    father_husband_name = Column(String(200), nullable=True)
    previous_owner = Column(String(200), nullable=True)
    current_owner = Column(String(200), nullable=True)
    ownership_type = Column(String(100), default='Individual')

    survey_number = Column(String(100), index=True, nullable=False)
    khasra_number = Column(String(100), index=True, nullable=False)
    khata_number = Column(String(100), index=True, nullable=False)
    plot_number = Column(String(100), nullable=True)

    village = Column(String(100), index=True, nullable=False)
    tehsil = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=False)
    state = Column(String(100), default='Madhya Pradesh', nullable=False)

    land_area = Column(Float, nullable=False)  # in Acres / default unit
    area_unit = Column(String(50), default='Acres')
    land_classification = Column(String(100), default='Agricultural')

    registration_number = Column(String(100), unique=True, index=True, nullable=False)
    registration_date = Column(String(50), nullable=False)
    mutation_number = Column(String(100), nullable=True)
    document_type = Column(String(100), default='Sale Deed')

    # Status tracking
    status = Column(String(50), default='APPROVED', index=True)
    verification_status = Column(String(50), default='Verified')
    publication_status = Column(String(50), default='PUBLISHED')
    document_status = Column(String(100), default='Digitized and Verified')
    is_public = Column(Boolean, default=True)

    confidence_score = Column(Float, default=95.0)
    source_type = Column(String(50), default='HISTORICAL')
    coordinates_geojson = Column(JSON, nullable=True)
    last_verification_date = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Aliases for compatibility with newer specifications
    @property
    def area(self):
        return self.land_area

    @property
    def father_name(self):
        return self.father_husband_name

    documents = relationship('Document', back_populates='land_record')
    extracted_fields = relationship('ExtractedField', back_populates='land_record')
    validation_results = relationship('ValidationResult', back_populates='land_record')
    verification_records = relationship('VerificationRecord', back_populates='land_record')
