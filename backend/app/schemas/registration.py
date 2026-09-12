from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RegistrationBase(BaseModel):
    registration_number: str
    owner_name: str
    father_husband_name: Optional[str] = None
    survey_number: str
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    village: str
    tehsil: str
    district: str
    state: str = "Madhya Pradesh"
    land_area: float
    land_classification: Optional[str] = "Agricultural"

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationOut(RegistrationBase):
    id: int
    source: str
    registration_date: str
    expected_public_date: str
    document_name: Optional[str] = None
    status: str
    confidence_score: float
    has_mismatch: bool
    mismatch_details: Optional[str] = None
    land_record_id: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PipelineProcessResponse(BaseModel):
    registration_id: int
    registration_number: str
    pipeline_status: str
    stages_completed: list
    confidence_score: float
    has_mismatch: bool
    mismatch_details: Optional[str] = None
    message: str
