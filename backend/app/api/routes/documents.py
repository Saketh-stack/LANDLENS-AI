from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles, get_current_user
from backend.app.schemas.document import DocumentOut, DocumentUploadResponse
from backend.app.services.document_service import DocumentService
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
        job_id=doc.job_id,
        filename=doc.filename,
        file_size=doc.file_size or 0,
        file_hash=doc.file_hash or "",
        quality_score=doc.quality_score,
        ocr_status=doc.ocr_status,
        message="Document uploaded and processed via intelligent extraction pipeline."
    )

@router.get("/pending", response_model=List[DocumentOut])
def get_pending_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.get_pending_documents(db)

@router.post("/{id}/process")
def process_document_pipeline(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.run_pipeline(id, db)

@router.get("/{id}/ocr")
def get_document_ocr(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.get_document_ocr(id, db)

@router.get("/{id}/extraction")
def get_document_extraction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.get_document_extraction(id, db)

@router.get("/{id}/validation")
def get_document_validation(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.get_document_validation(id, db)

@router.get("/{id}/verification")
def get_document_verification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return DocumentService.get_document_verification(id, db)
