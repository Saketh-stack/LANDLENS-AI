from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.land_record import LandRecord
from backend.app.models.verification import VerificationRecord
from backend.app.models.ai_correction import AICorrection
from backend.app.models.extracted_field import ExtractedField
from backend.app.schemas.verification import VerificationActionRequest
from backend.app.services.audit_service import AuditService

class VerificationService:
    @staticmethod
    def get_verification_queue(db: Session) -> List[LandRecord]:
        return db.query(LandRecord).filter(
            LandRecord.status.in_(["OFFICER_REVIEW", "VALIDATION_PENDING", "LOW_CONFIDENCE", "VALIDATION_FAILED"])
        ).order_by(LandRecord.id.desc()).all()

    @staticmethod
    def process_officer_action(
        record_id: int,
        req: VerificationActionRequest,
        db: Session,
        officer_id: Optional[int] = None,
        officer_name: str = "Officer"
    ) -> Dict[str, Any]:
        record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land record not found")

        # Save AI Corrections if supplied
        if req.corrections:
            for c in req.corrections:
                orig_val = str(getattr(record, c.field_name, ""))
                setattr(record, c.field_name, c.corrected_value)
                correction = AICorrection(
                    field_name=c.field_name,
                    original_ai_value=orig_val,
                    corrected_value=c.corrected_value,
                    officer_name=officer_name
                )
                db.add(correction)

        # Apply action
        act = req.action.upper()
        if act == "APPROVED":
            record.status = "APPROVED"
            record.verification_status = "Verified"
            record.publication_status = "PUBLISHED"
            record.is_public = True
            record.last_verification_date = datetime.now().strftime("%d-%m-%Y")
        elif act == "REJECTED":
            record.status = "REJECTED"
            record.verification_status = "Rejected"
            record.publication_status = "REJECTED"
            record.is_public = False
        elif act == "SENT_BACK":
            record.status = "VALIDATION_PENDING"
            record.verification_status = "Sent Back"
            record.is_public = False
        elif act == "SYNC_CADASTRAL":
            record.status = "OFFICER_REVIEW"

        ver_rec = VerificationRecord(
            land_record_id=record.id,
            officer_id=officer_id,
            officer_name=officer_name,
            action=act,
            remarks=req.remarks
        )
        db.add(ver_rec)
        db.commit()

        AuditService.log_event(
            db=db,
            actor=officer_name,
            action=f"RECORD_{act}",
            entity_type="LAND_RECORD",
            entity_id=str(record.id),
            details=f"Record {record.registration_number} action '{act}'. Remarks: {req.remarks}"
        )

        return {
            "record_id": record.id,
            "status": record.status,
            "is_public": record.is_public,
            "message": f"Record {record.registration_number} updated to {record.status}."
        }
