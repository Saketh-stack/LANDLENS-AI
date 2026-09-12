from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles, get_current_user
from backend.app.schemas.registration import RegistrationOut, PipelineProcessResponse
from backend.app.services.registration_service import RegistrationService
from backend.app.models.user import User

router = APIRouter(prefix="/api/registrations", tags=["Registrations"])

@router.get("", response_model=List[RegistrationOut])
def get_registrations(db: Session = Depends(get_db)):
    return RegistrationService.list_registrations(db)

@router.post("/simulate", response_model=RegistrationOut, dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def simulate_registration(db: Session = Depends(get_db)):
    return RegistrationService.simulate_registration(db)

@router.post("/{id}/process-pipeline", response_model=PipelineProcessResponse, dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def process_pipeline(id: int, db: Session = Depends(get_db)):
    return RegistrationService.process_pipeline(id, db)

@router.post("/{id}/approve", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def approve_registration(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rec = RegistrationService.approve_registration(id, db, officer_name=current_user.full_name)
    return {
        "message": f"Registration {id} successfully approved and published.",
        "land_record_id": rec.id,
        "is_public": rec.is_public
    }
