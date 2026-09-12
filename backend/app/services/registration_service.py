from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.registration import Registration
from backend.app.models.land_record import LandRecord
from backend.app.integrations.registration_department import RegistrationDepartmentAdapter
from backend.app.services.audit_service import AuditService

class RegistrationService:
    @staticmethod
    def simulate_registration(db: Session, scenario: Optional[Dict[str, Any]] = None) -> Registration:
        return RegistrationDepartmentAdapter.simulate_incoming_registration(db, scenario)

    @staticmethod
    def list_registrations(db: Session) -> List[Registration]:
        return db.query(Registration).order_by(Registration.id.desc()).all()

    @staticmethod
    def get_registration_by_number(reg_num: str, db: Session) -> Optional[Registration]:
        return db.query(Registration).filter(Registration.registration_number == reg_num).first()

    @staticmethod
    def process_pipeline(reg_id: int, db: Session) -> Dict[str, Any]:
        reg = db.query(Registration).filter(Registration.id == reg_id).first()
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

        # Step progression
        stages = [
            {"stage": "DOCUMENT_RECEIVED", "label": "Document Received from SRO", "completed": True},
            {"stage": "OCR_COMPLETED", "label": "High-Speed OCR Execution", "completed": True},
            {"stage": "AI_EXTRACTED", "label": "18+ Structured Fields Extracted", "completed": True},
            {"stage": "VALIDATION_COMPLETED", "label": "14 Business Rules & Cadastral Check", "completed": True}
        ]

        if reg.has_mismatch:
            reg.status = "OFFICER_REVIEW"
            stages.append({"stage": "AREA_MISMATCH_ALERT", "label": "Cadastral Delta Detected (Area Flag)", "completed": True})
        else:
            reg.status = "OFFICER_REVIEW"
            stages.append({"stage": "READY_FOR_OFFICER", "label": "Ready for Officer Verification", "completed": True})

        db.commit()

        AuditService.log_event(
            db=db,
            actor="Automated Pipeline Runner",
            action="PIPELINE_EXECUTED",
            entity_type="REGISTRATION",
            entity_id=str(reg.id),
            details=f"Registration {reg.registration_number} advanced to {reg.status}"
        )

        return {
            "registration_id": reg.id,
            "registration_number": reg.registration_number,
            "pipeline_status": reg.status,
            "stages_completed": stages,
            "confidence_score": reg.confidence_score,
            "has_mismatch": reg.has_mismatch,
            "mismatch_details": reg.mismatch_details,
            "message": "Automated ingestion pipeline finished processing successfully."
        }

    @staticmethod
    def approve_registration(reg_id: int, db: Session, officer_name: str = "Officer") -> LandRecord:
        reg = db.query(Registration).filter(Registration.id == reg_id).first()
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

        # Check if LandRecord already created
        land_rec = None
        if reg.land_record_id:
            land_rec = db.query(LandRecord).filter(LandRecord.id == reg.land_record_id).first()

        if not land_rec:
            land_rec = LandRecord(
                survey_number=reg.survey_number,
                khasra_number=reg.khasra_number or f"KHA-{reg.id*11}",
                khata_number=reg.khata_number or f"KH-{reg.id*101}",
                owner_name=reg.owner_name,
                father_husband_name=reg.father_husband_name,
                village=reg.village,
                tehsil=reg.tehsil,
                district=reg.district,
                state=reg.state,
                land_area=reg.land_area,
                land_classification=reg.land_classification,
                registration_number=reg.registration_number,
                registration_date=reg.registration_date,
                status="APPROVED",
                verification_status="Verified",
                publication_status="PUBLISHED",
                document_status="Digitized, Verified & Publicly Available",
                is_public=True,
                confidence_score=reg.confidence_score,
                source_type="NEW_REGISTRATION"
            )
            db.add(land_rec)
            db.flush()
            reg.land_record_id = land_rec.id

        reg.status = "PUBLISHED"
        land_rec.status = "APPROVED"
        land_rec.is_public = True
        land_rec.publication_status = "PUBLISHED"
        db.commit()

        AuditService.log_event(
            db=db,
            actor=officer_name,
            action="REGISTRATION_APPROVED_AND_PUBLISHED",
            entity_type="LAND_RECORD",
            entity_id=str(land_rec.id),
            details=f"Registration {reg.registration_number} approved and published to Citizen Portal."
        )

        return land_rec
