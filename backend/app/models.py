from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import  Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default='CITIZEN', nullable=False)  # CITIZEN, OFFICER, ADMIN
    department = Column(String(100), default='Revenue Department')
    designation = Column(String(100), default='Tahsildar / Land Records Officer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LandRecord(Base):
    __tablename__ = 'land_records'

    id = Column(Integer, primary_key=True, index=True)
    survey_number = Column(String(100), index=True, nullable=False)
    khasra_number = Column(String(100), index=True, nullable=False)
    khata_number = Column(String(100), index=True, nullable=False)
    plot_number = Column(String(100), nullable=True)
    
    owner_name = Column(String(200), index=True, nullable=False)
    father_husband_name = Column(String(200), nullable=True)
    previous_owner = Column(String(200), nullable=True)
    ownership_type = Column(String(100), default='Individual')  # Individual, Joint, Government, Community
    
    village = Column(String(100), index=True, nullable=False)
    tehsil = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=False)
    state = Column(String(100), default='Madhya Pradesh', nullable=False)
    
    land_area = Column(Float, nullable=False)  # in Acres
    land_classification = Column(String(100), default='Agricultural')  # Agricultural, Residential, Commercial, Industrial, Forest
    
    registration_number = Column(String(100), unique=True, index=True, nullable=False)
    registration_date = Column(String(50), nullable=False)
    mutation_number = Column(String(100), nullable=True)
    
    status = Column(String(50), default='APPROVED', index=True)  # RECEIVED, PROCESSING, OCR_COMPLETED, EXTRACTED, VALIDATION_PENDING, VALIDATION_FAILED, LOW_CONFIDENCE, OFFICER_REVIEW, APPROVED, REJECTED, PUBLISHED
    document_status = Column(String(100), default='Digitized and Verified')
    is_public = Column(Boolean, default=True)
    
    confidence_score = Column(Float, default=95.0)
    source_type = Column(String(50), default='HISTORICAL')  # HISTORICAL, NEW_REGISTRATION
    
    coordinates_geojson = Column(JSON, nullable=True)  # Mock cadastral polygon
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship('Document', back_populates='land_record')
    extracted_fields = relationship('ExtractedField', back_populates='land_record')
    validation_results = relationship('ValidationResult', back_populates='land_record')
    verification_records = relationship('VerificationRecord', back_populates='land_record')

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # PDF, JPG, PNG
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(100), index=True, nullable=True)
    phash = Column(String(64), index=True, nullable=True)
    preprocessed_file_path = Column(String(500), nullable=True)
    preprocessing_metadata = Column(JSON, nullable=True)
    job_id = Column(String(100), index=True, nullable=True)
    quality_score = Column(Float, nullable=True)
    document_type = Column(String(100), default='Sale Deed')  # Sale Deed, Khasra Khatauni, Cadastral Map, Mutation Sanction
    detected_language = Column(String(50), default='English')
    language = Column(String(50), default='English')
    ocr_status = Column(String(50), default='COMPLETED')
    ocr_raw_text = Column(Text, nullable=True)
    processing_status = Column(String(50), default='SUCCESS')
    uploaded_by = Column(String(100), default='Officer')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    land_record = relationship('LandRecord', back_populates='documents')

class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(100), unique=True, index=True, nullable=False)
    source = Column(String(100), default='Registration Department (Mock API)')
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
    expected_public_date = Column(String(50), nullable=False)  # Target 2-3 days
    
    document_name = Column(String(255), nullable=True)
    status = Column(String(50), default='RECEIVED')  # RECEIVED, OCR_COMPLETED, EXTRACTED, VALIDATION_COMPLETED, OFFICER_REVIEW, APPROVED, REJECTED, PUBLISHED
    confidence_score = Column(Float, default=92.0)
    has_mismatch = Column(Boolean, default=False)
    mismatch_details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    land_record_id = Column(Integer, ForeignKey('land_records.id'), nullable=True)

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
    confidence_tier = Column(String(20), default='HIGH')  # HIGH (>80%), MEDIUM (60-80%), LOW (<60%)
    requires_review = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    page_number = Column(Integer, default=1)
    ocr_confidence = Column(Float, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # x, y, w, h
    
    land_record = relationship('LandRecord', back_populates='extracted_fields')

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

class CadastralRecord(Base):
    __tablename__ = 'cadastral_records'

    id = Column(Integer, primary_key=True, index=True)
    survey_number = Column(String(100), unique=True, index=True, nullable=False)
    village = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    cadastral_area = Column(Float, nullable=False)  # Ground truth surveyed area
    survey_year = Column(Integer, default=2018)
    geometry_type = Column(String(50), default='Polygon')
    coordinates_geojson = Column(JSON, nullable=True)

class AICorrection(Base):
    __tablename__ = 'ai_corrections'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=True)
    field_name = Column(String(100), nullable=False)
    original_ai_value = Column(String(255), nullable=False)
    corrected_value = Column(String(255), nullable=False)
    officer_id = Column(Integer, nullable=True)
    officer_name = Column(String(150), default='Officer')
    reason = Column(String(255), nullable=True)
    language = Column(String(50), default='English')
    document_type = Column(String(100), default='Registered Sale Deed')
    timestamp = Column(DateTime, default=datetime.utcnow)

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
