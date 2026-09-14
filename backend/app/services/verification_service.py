from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.land_record import LandRecord
from backend.app.models.verification import VerificationRecord
from backend.app.models.ai_correction import AICorrection
from backend.app.models.extracted_field import ExtractedField
from backend.app.models.document import Document
from backend.app.schemas.verification import VerificationActionRequest
from backend.app.services.audit_service import AuditService

class VerificationService:
    @staticmethod
    def get_verification_queue(db: Session) -> List[LandRecord]:
        return db.query(LandRecord).filter(
            LandRecord.status.in_(["OFFICER_REVIEW", "VALIDATION_PENDING", "LOW_CONFIDENCE", "VALIDATION_FAILED", "USER_CORRECTED", "PROCESSING", "RECEIVED"])
        ).order_by(LandRecord.id.desc()).all()

    @classmethod
    def save_correction(
        cls,
        record_id: int,
        field_name: str,
        corrected_value: str,
        reason: Optional[str] = "Manual correction",
        officer_id: Optional[int] = None,
        officer_name: str = "Officer",
        db: Session = None
    ) -> Dict[str, Any]:
        record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land record not found")

        orig_val = str(getattr(record, field_name, "")) if hasattr(record, field_name) else ""

        # Update ExtractedField if present
        ext_field = db.query(ExtractedField).filter(
            ExtractedField.land_record_id == record.id,
            ExtractedField.field_name == field_name
        ).first()

        if ext_field:
            orig_val = ext_field.extracted_value or orig_val
            ext_field.corrected_value = corrected_value
            ext_field.is_verified = True
            ext_field.requires_review = False

        # Update record field
        if hasattr(record, field_name):
            try:
                if field_name == "land_area":
                    setattr(record, field_name, float(corrected_value))
                elif field_name in ["stamp_duty_paid", "market_value"]:
                    setattr(record, field_name, float(corrected_value))
                else:
                    setattr(record, field_name, corrected_value)
            except Exception:
                setattr(record, field_name, corrected_value)

        record.status = "USER_CORRECTED"

        # Find linked document to capture language and document_type
        doc = db.query(Document).filter(Document.land_record_id == record.id).first()
        doc_type = doc.document_type if doc else (record.document_type or "Registered Sale Deed")
        language = doc.language if doc else "English"
        doc_id = doc.id if doc else None

        correction = AICorrection(
            document_id=doc_id,
            field_name=field_name,
            original_ai_value=orig_val,
            corrected_value=corrected_value,
            officer_id=officer_id,
            officer_name=officer_name,
            reason=reason or "Officer correction",
            language=language,
            document_type=doc_type
        )
        db.add(correction)
        db.commit()

        AuditService.log_event(
            db=db,
            actor=officer_name,
            action="FIELD_CORRECTED",
            entity_type="LAND_RECORD",
            entity_id=str(record.id),
            details=f"Field '{field_name}' corrected from '{orig_val}' to '{corrected_value}'. Reason: {reason}"
        )

        return {
            "record_id": record.id,
            "field_name": field_name,
            "original_value": orig_val,
            "corrected_value": corrected_value,
            "status": record.status,
            "message": f"Field '{field_name}' updated and saved to AI training dataset."
        }

    @classmethod
    def approve_record(
        cls,
        record_id: int,
        remarks: str = "Officer verified and approved",
        officer_id: Optional[int] = None,
        officer_name: str = "Officer",
        db: Session = None
    ) -> Dict[str, Any]:
        record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land record not found")

        record.status = "APPROVED"
        record.verification_status = "Verified"
        record.publication_status = "PUBLISHED"
        record.is_public = True
        record.last_verification_date = datetime.now().strftime("%d-%m-%Y")

        # Mark extracted fields verified
        db.query(ExtractedField).filter(ExtractedField.land_record_id == record.id).update({
            ExtractedField.is_verified: True,
            ExtractedField.requires_review: False
        })

        ver_rec = VerificationRecord(
            land_record_id=record.id,
            officer_id=officer_id,
            officer_name=officer_name,
            action="APPROVED",
            remarks=remarks
        )
        db.add(ver_rec)
        db.commit()

        AuditService.log_event(
            db=db,
            actor=officer_name,
            action="RECORD_APPROVED",
            entity_type="LAND_RECORD",
            entity_id=str(record.id),
            details=f"Record {record.registration_number} APPROVED and published to citizen portal. Remarks: {remarks}"
        )

        return {
            "record_id": record.id,
            "registration_number": record.registration_number,
            "status": record.status,
            "is_public": record.is_public,
            "message": f"Land Record {record.registration_number} successfully verified and published to Citizen Portal."
        }

    @classmethod
    def reject_record(
        cls,
        record_id: int,
        remarks: str = "Record rejected by verification officer",
        officer_id: Optional[int] = None,
        officer_name: str = "Officer",
        db: Session = None
    ) -> Dict[str, Any]:
        record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land record not found")

        record.status = "REJECTED"
        record.verification_status = "Rejected"
        record.publication_status = "REJECTED"
        record.is_public = False

        ver_rec = VerificationRecord(
            land_record_id=record.id,
            officer_id=officer_id,
            officer_name=officer_name,
            action="REJECTED",
            remarks=remarks
        )
        db.add(ver_rec)
        db.commit()

        AuditService.log_event(
            db=db,
            actor=officer_name,
            action="RECORD_REJECTED",
            entity_type="LAND_RECORD",
            entity_id=str(record.id),
            details=f"Record {record.registration_number} REJECTED. Remarks: {remarks}"
        )

        return {
            "record_id": record.id,
            "registration_number": record.registration_number,
            "status": record.status,
            "is_public": record.is_public,
            "message": f"Land Record {record.registration_number} rejected. Remarks: {remarks}"
        }

    @classmethod
    def export_corrections_dataset(cls, db: Session, limit: int = 1000) -> List[Dict[str, Any]]:
        corrections = db.query(AICorrection).order_by(AICorrection.id.desc()).limit(limit).all()
        results = []
        for c in corrections:
            results.append({
                "id": c.id,
                "document_id": c.document_id,
                "field_name": c.field_name,
                "original_ai_value": c.original_ai_value,
                "corrected_value": c.corrected_value,
                "officer_name": c.officer_name,
                "reason": c.reason,
                "language": c.language,
                "document_type": c.document_type,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None
            })
        return results

    @classmethod
    def process_officer_action(
        cls,
        record_id: int,
        req: VerificationActionRequest,
        db: Session,
        officer_id: Optional[int] = None,
        officer_name: str = "Officer"
    ) -> Dict[str, Any]:
        act = req.action.upper()
        if act == "APPROVED" or act == "USER_VERIFIED":
            # Save any corrections first
            if req.corrections:
                for c in req.corrections:
                    cls.save_correction(
                        record_id=record_id,
                        field_name=c.field_name,
                        corrected_value=c.corrected_value,
                        reason="Correction before approval",
                        officer_id=officer_id,
                        officer_name=officer_name,
                        db=db
                    )
            return cls.approve_record(record_id, req.remarks or "Verified", officer_id, officer_name, db)
        elif act == "REJECTED":
            return cls.reject_record(record_id, req.remarks or "Rejected", officer_id, officer_name, db)
        elif act == "SAVE_CHANGES":
            if req.corrections:
                for c in req.corrections:
                    cls.save_correction(
                        record_id=record_id,
                        field_name=c.field_name,
                        corrected_value=c.corrected_value,
                        reason=req.remarks or "Officer edit",
                        officer_id=officer_id,
                        officer_name=officer_name,
                        db=db
                    )
            rec = db.query(LandRecord).filter(LandRecord.id == record_id).first()
            return {
                "record_id": record_id,
                "status": rec.status if rec else "USER_CORRECTED",
                "message": "Changes saved as draft"
            }
        else:
            return cls.approve_record(record_id, req.remarks or "Action applied", officer_id, officer_name, db)
