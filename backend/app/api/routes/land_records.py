from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles, get_current_user
from backend.app.schemas.land_record import LandRecordOut, LandRecordCreate, LandRecordUpdate
from backend.app.services.land_record_service import LandRecordService
from backend.app.models.user import User

router = APIRouter(prefix="/api/land-records", tags=["Land Records"])

@router.get("", response_model=List[LandRecordOut])
def get_land_records(
    q: Optional[str] = Query(None),
    village: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))
):
    return LandRecordService.get_public_records(db=db, q=q, village=village, district=district, limit=limit)

@router.get("/{id}", response_model=LandRecordOut)
def get_land_record_detail(id: int, db: Session = Depends(get_db)):
    rec = LandRecordService.get_record_by_id(id, db)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land record not found")
    return rec

@router.post("", response_model=LandRecordOut, dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def create_land_record(data: LandRecordCreate, db: Session = Depends(get_db)):
    return LandRecordService.create_record(data, db)

@router.put("/{id}", response_model=LandRecordOut, dependencies=[Depends(require_roles(["OFFICER", "LAND_RECORD_OFFICER", "ADMIN"]))])
def update_land_record(id: int, data: LandRecordUpdate, db: Session = Depends(get_db)):
    rec = LandRecordService.update_record(id, data, db)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land record not found")
    return rec
