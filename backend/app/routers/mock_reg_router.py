from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.database import  get_db
from backend.app.models import  Registration, LandRecord, CadastralRecord, AuditLog
from backend.app.services.mock_dept import MockRegistrationDepartmentService
from backend.app.services.validation_engine import ValidationEngineService
from backend.app.services.ai_extractor import AIExtractorService

router = APIRouter(prefix="/api/mock-registration", tags=["Mock Registration Department"])

class SimulationRequest(BaseModel):
    scenario: Optional[str] = "standard"  # standard, duplicate_survey, area_mismatch, low_confidence

@router.post("/simulate")
def simulate_new_registration(req: SimulationRequest, db: Session = Depends(get_db)):
    """
    Simulates external Registration Department generating a new property registration,
    and pushing it to DoLR Land Record System via Mock API.
    """
    reg = MockRegistrationDepartmentService.simulate_incoming_registration(db, scenario=req.scenario)
    return {
        "status": "success",
        "message": "New registration received from Registration Department API",
        "registration": {
            "id": reg.id,
            "registration_number": reg.registration_number,
            "source": reg.source,
            "owner_name": reg.owner_name,
            "father_husband_name": reg.father_husband_name,
            "survey_number": reg.survey_number,
            "khasra_number": reg.khasra_number,
            "khata_number": reg.khata_number,
            "village": reg.village,
            "tehsil": reg.tehsil,
            "district": reg.district,
            "land_area": reg.land_area,
            "land_classification": reg.land_classification,
            "registration_date": reg.registration_date,
            "expected_public_date": reg.expected_public_date,
            "document_name": reg.document_name,
            "status": reg.status,
            "confidence_score": reg.confidence_score
        }
    }

@router.get("/list")
def list_registrations(db: Session = Depends(get_db)):
    registrations = db.query(Registration).order_by(Registration.id.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "registration_number": r.registration_number,
            "source": r.source,
            "owner_name": r.owner_name,
            "survey_number": r.survey_number,
            "village": r.village,
            "district": r.district,
            "land_area": r.land_area,
            "registration_date": r.registration_date,
            "expected_public_date": r.expected_public_date,
            "status": r.status,
            "confidence_score": r.confidence_score,
            "has_mismatch": r.has_mismatch,
            "mismatch_details": r.mismatch_details
        }
        for r in registrations
    ]

@router.post("/{reg_id}/process-pipeline")
def run_automatic_processing_pipeline(reg_id: int, db: Session = Depends(get_db)):
    """
    Simulates the automatic end-to-end processing pipeline:
    Registration Dept -> Document Received -> OCR -> AI Extraction -> Validation -> Confidence Scoring -> Officer Verification
    """
    reg = db.query(Registration).filter(Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Step 1: AI & Validation check
    record_dict = {
        "owner_name": reg.owner_name,
        "survey_number": reg.survey_number,
        "village": reg.village,
        "district": reg.district,
        "land_area": reg.land_area,
        "registration_number": reg.registration_number,
        "registration_date": reg.registration_date
    }
    validation = ValidationEngineService.validate_record(record_dict, db)

    # Check cadastral mismatch specifically (e.g., 2.45 vs 2.40)
    cadastral = db.query(CadastralRecord).filter(CadastralRecord.survey_number == reg.survey_number).first()
    has_mismatch = False
    mismatch_msg = ""
    if cadastral and abs(reg.land_area - cadastral.cadastral_area) > 0.02:
        has_mismatch = True
        mismatch_msg = f"Area mismatch: Registration = {reg.land_area:.2f} Acres, Cadastral DB = {cadastral.cadastral_area:.2f} Acres"
        reg.has_mismatch = True
        reg.mismatch_details = mismatch_msg

    # Create corresponding LandRecord awaiting officer verification
    land_record = LandRecord(
        survey_number=reg.survey_number,
        khasra_number=reg.khasra_number or f"KHA-{reg.id * 111}",
        khata_number=reg.khata_number or f"KH-{reg.id * 222}",
        plot_number=f"PLOT-{reg.id * 7}",
        owner_name=reg.owner_name,
        father_husband_name=reg.father_husband_name,
        previous_owner="State / Prior Owner",
        ownership_type="Individual",
        village=reg.village,
        tehsil=reg.tehsil,
        district=reg.district,
        state=reg.state,
        land_area=reg.land_area,
        land_classification=reg.land_classification,
        registration_number=reg.registration_number,
        registration_date=reg.registration_date,
        status="OFFICER_REVIEW" if not validation["has_errors"] else "VALIDATION_FAILED",
        document_status="Waiting for Officer Verification",
        is_public=False, # Strictly NOT public until approved!
        confidence_score=reg.confidence_score,
        source_type="NEW_REGISTRATION"
    )
    db.add(land_record)
    db.flush()

    reg.land_record_id = land_record.id
    reg.status = "OFFICER_REVIEW"
    
    # Audit log
    audit = AuditLog(
        actor="AI Digitization Pipeline",
        actor_role="SYSTEM",
        action="AUTO_PROCESSING_COMPLETED",
        entity_type="REGISTRATION",
        entity_id=reg.registration_number,
        details=f"Processed registration {reg.registration_number}. Validation status: {validation['overall_status']}. Mismatch: {mismatch_msg or 'None'}"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "registration_id": reg.id,
        "land_record_id": land_record.id,
        "pipeline_events": [
            {"label": "Document Received from Registration Dept", "status": "DONE"},
            {"label": "OCR Completed (Indic/English Engine)", "status": "DONE"},
            {"label": "AI Field Extraction Performed", "status": "DONE"},
            {"label": "Business-Rule Validation Completed", "status": "DONE"},
            {"label": "Confidence Scoring Generated (94.2%)", "status": "DONE"},
            {"label": "Cross-Database Cadastral Check", "status": "FLAGGED" if has_mismatch else "DONE"},
            {"label": "Waiting for Officer Verification", "status": "ACTIVE"}
        ],
        "cadastral_mismatch": {
            "has_mismatch": has_mismatch,
            "message": mismatch_msg,
            "cadastral_area": cadastral.cadastral_area if cadastral else None,
            "registered_area": reg.land_area
        },
        "target_service_notice": "Proposed system target: Make verified registration records available for public viewing within 2-3 days."
    }

@router.post("/{reg_id}/approve")
def approve_new_registration(reg_id: int, db: Session = Depends(get_db)):
    """
    Officer completes verification and publishes registration to public portal
    """
    reg = db.query(Registration).filter(Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    reg.status = "PUBLISHED"
    
    # Update linked land record to PUBLISHED and is_public=True
    if reg.land_record_id:
        record = db.query(LandRecord).filter(LandRecord.id == reg.land_record_id).first()
        if record:
            record.status = "APPROVED"
            record.is_public = True
            record.document_status = "Digitized, Verified & Publicly Available"
    
    audit = AuditLog(
        actor="Officer Rajendra Prasad Sharma",
        actor_role="OFFICER",
        action="REGISTRATION_APPROVED_AND_PUBLISHED",
        entity_type="REGISTRATION",
        entity_id=reg.registration_number,
        details=f"New registration {reg.registration_number} published for public viewing on Citizen Portal."
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "message": f"Registration {reg.registration_number} verified and published to Public Portal!",
        "public_status": "Available for public viewing"
    }
