from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles, get_current_user
from backend.app.schemas.land_record import LandRecordOut
from backend.app.schemas.verification import VerificationActionRequest
from backend.app.services.verification_service import VerificationService
from backend.app.models.user import User

router = APIRouter(prefix="/api/verification", tags=["Verification"])

class CorrectionRequest(BaseModel):
    field_name: str
    corrected_value: str
    reason: Optional[str] = "Officer manual correction"

class OfficerRemarksRequest(BaseModel):
    remarks: Optional[str] = "Verified and approved by officer"

@router.get("/queue", response_model=List[LandRecordOut], dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def get_verification_queue(db: Session = Depends(get_db)):
    return VerificationService.get_verification_queue(db)

@router.post("/{id}/verify", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def process_verification(
    id: int,
    req: VerificationActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return VerificationService.process_officer_action(
        record_id=id,
        req=req,
        db=db,
        officer_id=current_user.id,
        officer_name=current_user.full_name
    )

@router.post("/{id}/correct", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def correct_field(
    id: int,
    req: CorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return VerificationService.save_correction(
        record_id=id,
        field_name=req.field_name,
        corrected_value=req.corrected_value,
        reason=req.reason,
        officer_id=current_user.id,
        officer_name=current_user.full_name,
        db=db
    )

@router.post("/{id}/approve", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def approve_record(
    id: int,
    req: OfficerRemarksRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    remarks = req.remarks if req else "Officer verified and approved"
    return VerificationService.approve_record(
        record_id=id,
        remarks=remarks,
        officer_id=current_user.id,
        officer_name=current_user.full_name,
        db=db
    )

@router.post("/{id}/reject", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def reject_record(
    id: int,
    req: OfficerRemarksRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    remarks = req.remarks if req else "Record rejected by verification officer"
    return VerificationService.reject_record(
        record_id=id,
        remarks=remarks,
        officer_id=current_user.id,
        officer_name=current_user.full_name,
        db=db
    )

@router.get("/corrections-dataset", dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def get_corrections_dataset(
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    return VerificationService.export_corrections_dataset(db=db, limit=limit)
