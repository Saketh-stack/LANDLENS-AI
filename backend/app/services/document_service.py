import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.models.land_record import LandRecord
from backend.app.models.extracted_field import ExtractedField
from backend.app.models.validation_result import ValidationResult
from backend.app.models.cadastral_record import CadastralRecord
from backend.app.core.config import settings
from backend.app.utils.file_utils import generate_secure_filename, validate_file_metadata
from backend.app.utils.hashing import compute_file_sha256
from backend.app.services.audit_service import AuditService
from backend.app.services.storage_service import StorageService
from backend.app.services.preprocessing_service import PreprocessingService
from backend.app.services.ocr_service import OCRService
from backend.app.services.region_detection_service import RegionDetectionService
from backend.app.ai.multilingual.extraction_service import MultilingualExtractionService
from backend.app.services.validation_engine import ValidationEngine
from backend.app.validation.duplicate_rules import DuplicateRulesEngine

class DocumentService:
    @staticmethod
    def get_upload_dir() -> str:
        upload_dir = os.path.abspath(settings.UPLOAD_DIR or "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @classmethod
    def get_document_disk_path(cls, doc: Document) -> str:
        upload_dir = cls.get_upload_dir()
        if doc.file_path.startswith("/uploads/"):
            rel_sub = doc.file_path[len("/uploads/"):].lstrip("/")
            return os.path.join(upload_dir, rel_sub)
        if os.path.isabs(doc.file_path):
            return doc.file_path
        return os.path.join(upload_dir, doc.filename)

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
        # 1. Read contents and validate
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
        job_id = f"JOB-{uuid.uuid4().hex[:12].upper()}"

        # 2. Image Preprocessing & Quality Analysis
        prep_res = PreprocessingService.preprocess(dest_path)
        quality_score = prep_res.get("quality_score", 85.0)
        phash = prep_res.get("dhash") or ""
        proc_image_path = prep_res.get("processed_image_path") or dest_path

        # Store preprocessed file relative path if generated
        proc_rel_path = f"/uploads/{os.path.basename(proc_image_path)}" if proc_image_path else f"/uploads/{secure_name}"

        # 3. Multilingual PaddleOCR / RapidOCR
        ocr_res = OCRService.process_document(proc_image_path)
        ocr_raw_text = ocr_res.get("text", "")
        ocr_language = ocr_res.get("language", "English")
        ocr_lines = ocr_res.get("lines", [])

        # 4. Create Document Record
        doc = Document(
            land_record_id=land_record_id,
            registration_id=registration_id,
            filename=secure_name,
            file_path=f"/uploads/{secure_name}",
            file_type=ext.upper(),
            file_size=file_size,
            file_hash=file_hash,
            phash=phash,
            preprocessed_file_path=proc_rel_path,
            preprocessing_metadata=prep_res.get("quality_metrics", {}),
            job_id=job_id,
            quality_score=quality_score,
            document_type=document_type,
            language=ocr_language,
            ocr_status="COMPLETED" if ocr_res.get("success") else "FAILED",
            ocr_raw_text=ocr_raw_text,
            processing_status="PROCESSING",
            uploaded_by=uploaded_by
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # 5. Run full pipeline (Extraction, Validation, Duplicates)
        cls.run_pipeline(doc.id, db)
        db.refresh(doc)

        AuditService.log_event(
            db=db,
            actor=uploaded_by,
            action="DOCUMENT_UPLOADED",
            entity_type="DOCUMENT",
            entity_id=str(doc.id),
            details=f"Document {file.filename} uploaded (SHA-256: {file_hash[:12]}..., Quality: {quality_score})"
        )

        return doc

    @classmethod
    def run_pipeline(cls, doc_id: int, db: Session) -> Dict[str, Any]:
        """
        Executes complete traceable pipeline:
        Preprocessing -> PaddleOCR -> Region Detection -> AI Field Extraction ->
        Cadastral Validation -> 8-Vector Duplicate Detection -> Save DB Records
        """
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        disk_path = cls.get_document_disk_path(doc)

        # 1. Preprocessing (if not done yet)
        if not doc.phash or not doc.quality_score:
            prep_res = PreprocessingService.preprocess(disk_path)
            doc.quality_score = prep_res.get("quality_score", 85.0)
            doc.phash = prep_res.get("dhash") or ""
            doc.preprocessed_file_path = f"/uploads/{os.path.basename(prep_res.get('processed_image_path', disk_path))}"
            doc.preprocessing_metadata = prep_res.get("quality_metrics", {})
            db.commit()
        else:
            prep_res = {"quality_score": doc.quality_score, "quality_metrics": doc.preprocessing_metadata or {}}

        ocr_input_path = cls.get_upload_dir() + "/" + os.path.basename(doc.preprocessed_file_path) if doc.preprocessed_file_path else disk_path
        if not os.path.exists(ocr_input_path):
            ocr_input_path = disk_path

        # 2. OCR Execution (if raw text not populated)
        if not doc.ocr_raw_text or doc.ocr_status != "COMPLETED":
            ocr_res = OCRService.process_document(ocr_input_path)
            doc.ocr_raw_text = ocr_res.get("text", "")
            doc.language = ocr_res.get("language", "English")
            doc.ocr_status = "COMPLETED" if ocr_res.get("success") else "FAILED"
            db.commit()
        else:
            ocr_res = OCRService.process_document(ocr_input_path)

        # 3. Layout Region Detection
        regions = RegionDetectionService.detect_regions(ocr_res.get("lines", []))

        # 4. Field Extraction with Aliases & Confidence Tiers
        extraction = MultilingualExtractionService.extract_fields_sync(
            doc.ocr_raw_text or "",
            ocr_boxes=ocr_res.get("lines", [])
        )
        rec_data = extraction.get("record_data", {})
        fields_detailed = extraction.get("fields_detailed", [])

        # 5. Link or Create LandRecord
        record = None
        if doc.land_record_id:
            record = db.query(LandRecord).filter(LandRecord.id == doc.land_record_id).first()

        if not record:
            # Create a new LandRecord
            try:
                area_val = float(rec_data.get("land_area", 0.0))
            except (ValueError, TypeError):
                area_val = 0.0

            record = LandRecord(
                registration_number=rec_data.get("registration_number") or f"REG-DOC-{doc.id}",
                survey_number=rec_data.get("survey_number") or "N/A",
                khasra_number=rec_data.get("khasra_number"),
                khata_number=rec_data.get("khata_number"),
                owner_name=rec_data.get("owner_name") or "Awaiting Verification",
                father_husband_name=rec_data.get("father_husband_name"),
                land_area=area_val,
                land_classification=rec_data.get("land_type") or "Agricultural",
                plot_number=rec_data.get("plot_number"),
                village=rec_data.get("village") or "Unspecified",
                tehsil=rec_data.get("tehsil"),
                district=rec_data.get("district") or "Unspecified",
                state=rec_data.get("state") or "India",
                document_type=doc.document_type or "Sale Deed",
                registration_date=rec_data.get("registration_date"),
                stamp_duty_paid=float(rec_data.get("stamp_duty_paid", 0.0) or 0.0),
                market_value=float(rec_data.get("market_value", 0.0) or 0.0),
                confidence_score=extraction.get("confidence", 85.0),
                status="OFFICER_REVIEW" if extraction.get("requires_review") else "VALIDATION_PENDING",
                verification_status="Pending Officer Review",
                publication_status="DRAFT",
                is_public=False
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            doc.land_record_id = record.id
            db.commit()
        else:
            # Update existing record
            if rec_data.get("survey_number"):
                record.survey_number = rec_data.get("survey_number")
            if rec_data.get("owner_name"):
                record.owner_name = rec_data.get("owner_name")
            if rec_data.get("village"):
                record.village = rec_data.get("village")
            if rec_data.get("district"):
                record.district = rec_data.get("district")
            db.commit()

        # 6. Save ExtractedField Entries in DB
        db.query(ExtractedField).filter(ExtractedField.land_record_id == record.id).delete()
        for fld in fields_detailed:
            ef = ExtractedField(
                land_record_id=record.id,
                field_name=fld.get("field_name"),
                field_label=fld.get("field_label") or fld.get("field_name", "").replace("_", " ").title(),
                extracted_value=str(fld.get("extracted_value") or ""),
                source_text=fld.get("source_text"),
                confidence=float(fld.get("confidence") or 90.0),
                confidence_tier=fld.get("confidence_tier") or "HIGH",
                requires_review=bool(fld.get("requires_review", False)),
                is_verified=False,
                page_number=int(fld.get("page_number") or 1),
                ocr_confidence=float(fld.get("ocr_confidence") or 95.0),
                bounding_box=fld.get("bounding_box")
            )
            db.add(ef)
        db.commit()

        # 7. Run 14-Rule Statutory Validation
        val_res = ValidationEngine.validate_record(rec_data, db=db, current_record_id=record.id)
        db.query(ValidationResult).filter(ValidationResult.land_record_id == record.id).delete()
        for v in val_res.get("rules", []):
            db.add(ValidationResult(
                land_record_id=record.id,
                rule_id=v.get("rule", "RULE"),
                rule_name=v.get("rule", "RULE").replace("_", " ").title(),
                status=v.get("severity", "PASS"),
                message=v.get("message", ""),
                details=v
            ))
        db.commit()

        # 8. Run 8-Vector Duplicate Detection
        dup_res = DuplicateRulesEngine.analyze_duplicates(
            data=rec_data,
            db=db,
            current_record_id=record.id,
            file_hash=doc.file_hash,
            phash=doc.phash,
            raw_text=doc.ocr_raw_text,
            ocr_confidence=ocr_res.get("overall_confidence")
        )

        doc.processing_status = "SUCCESS"
        db.commit()

        return {
            "document_id": doc.id,
            "job_id": doc.job_id,
            "land_record_id": record.id,
            "preprocessing": prep_res,
            "ocr": {
                "language": ocr_res.get("language"),
                "confidence": ocr_res.get("overall_confidence"),
                "lines_count": len(ocr_lines)
            },
            "regions": regions,
            "extraction": extraction,
            "validation": val_res,
            "duplicate_check": dup_res,
            "status": "COMPLETED"
        }

    @classmethod
    def get_document(cls, doc_id: int, db: Session) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()

    @classmethod
    def get_pending_documents(cls, db: Session) -> List[Document]:
        return db.query(Document).filter(Document.processing_status != "SUCCESS").all()

    @classmethod
    def get_document_ocr(cls, doc_id: int, db: Session) -> Dict[str, Any]:
        doc = cls.get_document(doc_id, db)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        disk_path = cls.get_document_disk_path(doc)
        ocr_input = cls.get_upload_dir() + "/" + os.path.basename(doc.preprocessed_file_path) if doc.preprocessed_file_path else disk_path
        if not os.path.exists(ocr_input):
            ocr_input = disk_path

        ocr_res = OCRService.process_document(ocr_input)
        return {
            "document_id": doc.id,
            "language": doc.language or ocr_res.get("language", "English"),
            "ocr_confidence": ocr_res.get("overall_confidence", 95.0),
            "raw_text": doc.ocr_raw_text or ocr_res.get("text", ""),
            "lines": ocr_res.get("lines", []),
            "words_count": len((doc.ocr_raw_text or "").split())
        }

    @classmethod
    def get_document_extraction(cls, doc_id: int, db: Session) -> Dict[str, Any]:
        doc = cls.get_document(doc_id, db)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Check existing ExtractedField rows
        fields = db.query(ExtractedField).filter(ExtractedField.land_record_id == doc.land_record_id).all() if doc.land_record_id else []
        if fields:
            fields_detailed = []
            rec_data = {}
            for f in fields:
                val = f.corrected_value if f.corrected_value is not None else f.extracted_value
                rec_data[f.field_name] = val
                fields_detailed.append({
                    "id": f.id,
                    "field_name": f.field_name,
                    "field_label": f.field_label,
                    "extracted_value": f.extracted_value,
                    "corrected_value": f.corrected_value,
                    "source_text": f.source_text,
                    "confidence": f.confidence,
                    "confidence_tier": f.confidence_tier,
                    "requires_review": f.requires_review,
                    "page_number": f.page_number,
                    "ocr_confidence": f.ocr_confidence,
                    "bounding_box": f.bounding_box
                })
            return {
                "document_id": doc.id,
                "land_record_id": doc.land_record_id,
                "record_data": rec_data,
                "fields_detailed": fields_detailed,
                "requires_review": any(f.requires_review for f in fields)
            }

        # Otherwise extract on-the-fly
        return MultilingualExtractionService.extract_fields_sync(doc.ocr_raw_text or "")

    @classmethod
    def get_document_validation(cls, doc_id: int, db: Session) -> Dict[str, Any]:
        doc = cls.get_document(doc_id, db)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        if doc.land_record_id:
            val_records = db.query(ValidationResult).filter(ValidationResult.land_record_id == doc.land_record_id).all()
            if val_records:
                rules = []
                for vr in val_records:
                    rules.append({
                        "rule": vr.rule_id,
                        "rule_name": vr.rule_name,
                        "severity": vr.status,
                        "message": vr.message,
                        "passed": vr.status == "PASS"
                    })
                error_count = sum(1 for r in rules if r["severity"] == "ERROR")
                warn_count = sum(1 for r in rules if r["severity"] == "WARNING")
                return {
                    "document_id": doc.id,
                    "land_record_id": doc.land_record_id,
                    "is_valid": error_count == 0,
                    "error_count": error_count,
                    "warning_count": warn_count,
                    "rules": rules
                }

        # Fallback to validating extracted data
        ext = cls.get_document_extraction(doc_id, db)
        data = ext.get("record_data", {})
        return ValidationEngine.validate_record(data, db=db, current_record_id=doc.land_record_id)

    @classmethod
    def get_document_verification(cls, doc_id: int, db: Session) -> Dict[str, Any]:
        doc = cls.get_document(doc_id, db)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        record = db.query(LandRecord).filter(LandRecord.id == doc.land_record_id).first() if doc.land_record_id else None
        ext = cls.get_document_extraction(doc_id, db)
        val = cls.get_document_validation(doc_id, db)

        # Cadastral Ground Truth crosscheck
        cad = None
        if record and record.survey_number:
            cad = db.query(CadastralRecord).filter(CadastralRecord.survey_number == record.survey_number).first()

        cadastral_crosscheck = {
            "exists_in_cadastral": bool(cad is not None),
            "cadastral_owner": cad.owner_name if cad else None,
            "cadastral_area": cad.cadastral_area if cad else None,
            "area_mismatch": bool(cad and record and abs(record.land_area - cad.cadastral_area) > 0.05),
            "area_delta": round(abs(record.land_area - cad.cadastral_area), 2) if (cad and record) else 0.0
        }

        # Duplicate risk check
        dup = DuplicateRulesEngine.analyze_duplicates(
            data=ext.get("record_data", {}),
            db=db,
            current_record_id=record.id if record else None,
            file_hash=doc.file_hash,
            phash=doc.phash,
            raw_text=doc.ocr_raw_text
        )

        return {
            "document_id": doc.id,
            "land_record_id": record.id if record else None,
            "record": record,
            "document_url": doc.preprocessed_file_path or doc.file_path,
            "original_file_path": doc.file_path,
            "preprocessed_file_path": doc.preprocessed_file_path,
            "quality_score": doc.quality_score,
            "language": doc.language,
            "extracted_fields": ext.get("fields_detailed", []),
            "validation": val,
            "cadastral_crosscheck": cadastral_crosscheck,
            "duplicate_risk": dup,
            "requires_review": ext.get("requires_review", False) or cadastral_crosscheck.get("area_mismatch", False) or dup.get("is_duplicate", False)
        }
