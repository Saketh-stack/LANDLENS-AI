from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles, get_current_user
from backend.app.schemas.document import DocumentOut, DocumentUploadResponse
from backend.app.services.document_service import DocumentService
from backend.app.ai.extraction_service import ExtractionService
from backend.app.models.user import User

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("Sale Deed"),
    land_record_id: Optional[int] = Form(None),
    registration_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    doc = await DocumentService.upload_and_process_document(
        file=file,
        db=db,
        uploaded_by=current_user.full_name,
        land_record_id=land_record_id,
        registration_id=registration_id,
        document_type=document_type
    )
    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        file_size=doc.file_size or 0,
        file_hash=doc.file_hash or "",
        ocr_status=doc.ocr_status,
        message="Document uploaded and processed via OCR engine."
    )

@router.get("/pending", response_model=List[DocumentOut])
def get_pending_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.get_pending_documents(db)

@router.post("/{id}/process")
async def process_document_pipeline(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    doc = DocumentService.get_document(id, db)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    extraction = await ExtractionService.extract_fields_from_text(doc.ocr_raw_text or "")
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "processing_status": "COMPLETED",
        "extraction": extraction
    }

@router.get("/{id}/extraction")
def get_document_extraction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    doc = DocumentService.get_document(id, db)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return ExtractionService.extract_fields_sync(doc.ocr_raw_text or "")
