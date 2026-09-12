from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class FieldCorrectionRequest(BaseModel):
    field_name: str
    corrected_value: str

class VerificationActionRequest(BaseModel):
    action: str  # APPROVED, REJECTED, SENT_BACK, SYNC_CADASTRAL
    remarks: Optional[str] = "Verification processed by revenue officer"
    corrections: Optional[List[FieldCorrectionRequest]] = []

class VerificationHistoryOut(BaseModel):
    id: int
    land_record_id: Optional[int] = None
    registration_id: Optional[int] = None
    officer_name: str
    action: str
    remarks: Optional[str] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
