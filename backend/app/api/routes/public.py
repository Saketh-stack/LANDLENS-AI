from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from backend.app.core.database import get_db
from backend.app.models.land_record import LandRecord
from backend.app.models.registration import Registration
from backend.app.schemas.land_record import LandRecordPublicOut
from backend.app.services.land_record_service import LandRecordService
from backend.app.services.search_service import SearchService

router = APIRouter(prefix="/api/public", tags=["Public Citizen Portal"])

@router.get("/records", response_model=List[LandRecordPublicOut])
@router.get("/land-records", response_model=List[LandRecordPublicOut])
def get_public_land_records(
    q: Optional[str] = Query(None),
    owner_name: Optional[str] = Query(None),
    survey_number: Optional[str] = Query(None),
    khasra_number: Optional[str] = Query(None),
    khata_number: Optional[str] = Query(None),
    village: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    STRICT SECURITY RULE: Only returns APPROVED & PUBLISHED records.
    Unapproved, processing, or rejected records are never exposed to citizens.
    """
    return LandRecordService.get_public_records(
        db=db,
        q=q,
        owner_name=owner_name,
        survey_number=survey_number,
        khasra_number=khasra_number,
        khata_number=khata_number,
        village=village,
        district=district
    )

@router.get("/land-records/{id}", response_model=LandRecordPublicOut)
@router.get("/records/{id}", response_model=LandRecordPublicOut)
def get_public_land_record_detail(id: int, db: Session = Depends(get_db)):
    rec = db.query(LandRecord).filter(
        LandRecord.id == id,
        LandRecord.is_public == True,
        LandRecord.status.in_(["APPROVED", "PUBLISHED", "USER_VERIFIED"])
    ).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certified Record of Rights (RoR) not found or pending verification."
        )
    return rec

@router.get("/search", response_model=List[LandRecordPublicOut])
def search_public_records(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return SearchService.search_all_records(query_str=q, db=db, include_internal=False)

@router.get("/registration-status/{registration_number}")
def get_registration_status(registration_number: str, db: Session = Depends(get_db)):
    # Look in LandRecord first
    rec = db.query(LandRecord).filter(
        LandRecord.registration_number.ilike(registration_number),
        LandRecord.is_public == True
    ).first()
    if rec:
        return {
            "registration_number": rec.registration_number,
            "status": "PUBLISHED",
            "document_status": "Digitized, Verified & Publicly Available",
            "owner_name": rec.owner_name,
            "survey_number": rec.survey_number,
            "village": rec.village,
            "district": rec.district,
            "land_record_id": rec.id,
            "public_available": True
        }

    # Otherwise look in pending registrations
    reg = db.query(Registration).filter(
        Registration.registration_number.ilike(registration_number)
    ).first()
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration number not found")

    return {
        "registration_number": reg.registration_number,
        "status": reg.status,
        "source": reg.source,
        "owner_name": reg.owner_name,
        "survey_number": reg.survey_number,
        "village": reg.village,
        "district": reg.district,
        "expected_public_date": reg.expected_public_date,
        "public_available": False,
        "message": "Record is currently progressing through verification pipeline."
    }

@router.get("/stats")
def get_public_stats(db: Session = Depends(get_db)):
    verified_count = db.query(LandRecord).filter(
        LandRecord.status.in_(["APPROVED", "PUBLISHED", "USER_VERIFIED"]),
        LandRecord.is_public == True
    ).count()
    districts_count = db.query(func.count(func.distinct(LandRecord.district))).filter(
        LandRecord.district.isnot(None),
        LandRecord.district != "",
        LandRecord.district != "Not found"
    ).scalar() or 1
    villages_count = db.query(func.count(func.distinct(LandRecord.village))).filter(
        LandRecord.village.isnot(None),
        LandRecord.village != "",
        LandRecord.village != "Not found"
    ).scalar() or 1
    states_count = db.query(func.count(func.distinct(LandRecord.state))).filter(
        LandRecord.state.isnot(None),
        LandRecord.state != "",
        LandRecord.state != "Not found"
    ).scalar() or 1

    return {
        "total_verified_records": verified_count,
        "villages_covered": villages_count,
        "districts_active": districts_count,
        "states_onboarded": states_count,
        "system_status": "OPERATIONAL",
        "service_target": "Verified records made publicly accessible within 2-3 days"
    }
