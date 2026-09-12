from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.registration import RegistrationOut, PipelineProcessResponse
from backend.app.services.registration_service import RegistrationService
from backend.app.models.registration import Registration

router = APIRouter(prefix="/api/mock-registration", tags=["Mock Registration Department"])

@router.get("/list", response_model=List[RegistrationOut])
@router.get("", response_model=List[RegistrationOut])
def list_registrations(db: Session = Depends(get_db)):
    return RegistrationService.list_registrations(db)

@router.post("/simulate", response_model=RegistrationOut)
def simulate_registration(db: Session = Depends(get_db)):
    return RegistrationService.simulate_registration(db)

@router.post("/{id}/process-pipeline", response_model=PipelineProcessResponse)
def process_pipeline(id: int, db: Session = Depends(get_db)):
    return RegistrationService.process_pipeline(id, db)

@router.post("/{id}/approve")
def approve_registration(id: int, db: Session = Depends(get_db)):
    rec = RegistrationService.approve_registration(id, db, officer_name="Officer Rajendra Prasad")
    return {
        "message": f"Registration {id} approved and published to Citizen Portal.",
        "land_record_id": rec.id,
        "is_public": rec.is_public
    }
