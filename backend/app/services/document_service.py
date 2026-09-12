import os
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.document import Document
from backend.app.core.config import settings
from backend.app.utils.file_utils import generate_secure_filename, validate_file_metadata
from backend.app.utils.hashing import compute_file_sha256
from backend.app.ai.ocr_service import OCRService
from backend.app.services.audit_service import AuditService

class DocumentService:
    @staticmethod
    def get_upload_dir() -> str:
        upload_dir = os.path.abspath(settings.UPLOAD_DIR)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @classmethod
    async def upload_and_process_document(
        cls,
        file: UploadFile,
        db: Session,
        uploaded_by: str = "Officer",
        land_record_id: Optional[int] = None,
        registration_id: Optional[int] = None,
        document_type: str = "Sale Deed"
    ) -> Document:
        # Read contents
        contents = await file.read()
        file_size = len(contents)
        valid, msg = validate_file_metadata(file.filename, file_size)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        secure_name, ext = generate_secure_filename(file.filename)
        upload_dir = cls.get_upload_dir()
        dest_path = os.path.join(upload_dir, secure_name)

        with open(dest_path, "wb") as f:
            f.write(contents)

        file_hash = compute_file_sha256(dest_path)

        # Run OCR extraction
        ocr_engine = OCRService()
        ocr_res = ocr_engine.process_image(dest_path)

        doc = Document(
            land_record_id=land_record_id,
            registration_id=registration_id,
            filename=secure_name,
            file_path=f"/uploads/{secure_name}",
            file_type=ext.upper(),
            file_size=file_size,
            file_hash=file_hash,
            document_type=document_type,
            language=ocr_res.get("language", "English"),
            ocr_status="COMPLETED" if ocr_res.get("success") else "FAILED",
            ocr_raw_text=ocr_res.get("text", ""),
            processing_status="SUCCESS",
            uploaded_by=uploaded_by
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        AuditService.log_event(
            db=db,
            actor=uploaded_by,
            action="DOCUMENT_UPLOADED",
            entity_type="DOCUMENT",
            entity_id=str(doc.id),
            details=f"Document {file.filename} uploaded and hashed (SHA-256: {file_hash[:12]}...)"
        )

        return doc

    @staticmethod
    def get_document(doc_id: int, db: Session) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()

    @staticmethod
    def get_pending_documents(db: Session) -> List[Document]:
        return db.query(Document).filter(Document.processing_status != "SUCCESS").all()
