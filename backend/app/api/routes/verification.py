from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles, get_current_user
from backend.app.schemas.land_record import LandRecordOut
from backend.app.schemas.verification import VerificationActionRequest
from backend.app.services.verification_service import VerificationService
from backend.app.models.user import User

router = APIRouter(prefix="/api/verification", tags=["Verification"])

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
