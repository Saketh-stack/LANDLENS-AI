from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LandRecordBase(BaseModel):
    survey_number: str
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None
    owner_name: str
    father_husband_name: Optional[str] = None
    previous_owner: Optional[str] = None
    current_owner: Optional[str] = None
    ownership_type: Optional[str] = "Individual"
    village: str
    tehsil: str
    district: str
    state: str = "Madhya Pradesh"
    land_area: float
    area_unit: Optional[str] = "Acres"
    land_classification: Optional[str] = "Agricultural"
    registration_number: str
    registration_date: str
    mutation_number: Optional[str] = None
    document_type: Optional[str] = "Sale Deed"

class LandRecordCreate(LandRecordBase):
    coordinates_geojson: Optional[Dict[str, Any]] = None

class LandRecordUpdate(BaseModel):
    owner_name: Optional[str] = None
    land_area: Optional[float] = None
    land_classification: Optional[str] = None
    verification_status: Optional[str] = None
    publication_status: Optional[str] = None
    status: Optional[str] = None

class LandRecordOut(LandRecordBase):
    id: int
    status: str
    verification_status: Optional[str] = None
    publication_status: Optional[str] = None
    document_status: Optional[str] = None
    is_public: bool
    confidence_score: Optional[float] = 95.0
    coordinates_geojson: Optional[Dict[str, Any]] = None
    last_verification_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class LandRecordPublicOut(BaseModel):
    id: int
    owner_name: str
    father_husband_name: Optional[str] = None
    survey_number: str
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None
    village: str
    tehsil: str
    district: str
    state: str
    land_area: float
    land_classification: str
    registration_number: str
    registration_date: str
    status: str
    document_status: Optional[str] = None
    verification_status: Optional[str] = None
    last_verification_date: Optional[str] = None
    coordinates_geojson: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

