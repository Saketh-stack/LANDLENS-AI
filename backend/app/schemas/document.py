from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentOut(BaseModel):
    id: int
    land_record_id: Optional[int] = None
    registration_id: Optional[int] = None
    filename: str
    file_path: str
    file_type: str
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    document_type: Optional[str] = "Sale Deed"
    language: Optional[str] = "English"
    ocr_status: str
    ocr_raw_text: Optional[str] = None
    processing_status: str
    uploaded_by: Optional[str] = "Officer"
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    file_size: int
    file_hash: str
    ocr_status: str
    message: str
