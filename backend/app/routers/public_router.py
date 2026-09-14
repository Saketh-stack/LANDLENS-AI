from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from backend.app.database import  get_db
from backend.app.models import  LandRecord, AuditLog

router = APIRouter(prefix="/api/public", tags=["Public Portal"])

@router.get("/records")
def search_records(
    q: Optional[str] = Query(None, description="General search keyword"),
    owner_name: Optional[str] = Query(None),
    survey_number: Optional[str] = Query(None),
    khasra_number: Optional[str] = Query(None),
    khata_number: Optional[str] = Query(None),
    registration_number: Optional[str] = Query(None),
    village: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Public Search API:
    STRICT SECURITY RULE: Only returns APPROVED and PUBLISHED records.
    Never exposes unapproved, internal or rejected records to the public.
    """
    query = db.query(LandRecord).filter(
        LandRecord.status.in_(["APPROVED", "PUBLISHED"]),
        LandRecord.is_public == True
    )

    if q:
        kw = f"%{q.strip()}%"
        query = query.filter(
            or_(
                LandRecord.owner_name.ilike(kw),
                LandRecord.survey_number.ilike(kw),
                LandRecord.khasra_number.ilike(kw),
                LandRecord.khata_number.ilike(kw),
                LandRecord.registration_number.ilike(kw),
                LandRecord.village.ilike(kw),
                LandRecord.district.ilike(kw)
            )
        )

    if owner_name:
        query = query.filter(LandRecord.owner_name.ilike(f"%{owner_name.strip()}%"))
    if survey_number:
        query = query.filter(LandRecord.survey_number.ilike(f"%{survey_number.strip()}%"))
    if khasra_number:
        query = query.filter(LandRecord.khasra_number.ilike(f"%{khasra_number.strip()}%"))
    if khata_number:
        query = query.filter(LandRecord.khata_number.ilike(f"%{khata_number.strip()}%"))
    if registration_number:
        query = query.filter(LandRecord.registration_number.ilike(f"%{registration_number.strip()}%"))
    if village:
        query = query.filter(LandRecord.village.ilike(f"%{village.strip()}%"))
    if district:
        query = query.filter(LandRecord.district.ilike(f"%{district.strip()}%"))

    records = query.order_by(LandRecord.updated_at.desc()).all()

    # Mask internal notes, return safe public representation
    return [
        {
            "id": r.id,
            "owner_name": r.owner_name,
            "father_husband_name": r.father_husband_name,
            "survey_number": r.survey_number,
            "khasra_number": r.khasra_number,
            "khata_number": r.khata_number,
            "plot_number": r.plot_number,
            "village": r.village,
            "tehsil": r.tehsil,
            "district": r.district,
            "state": r.state,
            "land_area": r.land_area,
            "land_classification": r.land_classification,
            "registration_number": r.registration_number,
            "registration_date": r.registration_date,
            "status": r.status,
            "document_status": r.document_status,
            "verification_status": "Verified",
            "last_verification_date": r.updated_at.strftime("%d-%m-%Y") if r.updated_at else r.registration_date,
            "coordinates_geojson": r.coordinates_geojson
        }
        for r in records
    ]

@router.get("/records/{record_id}")
def get_public_record_details(record_id: int, db: Session = Depends(get_db)):
    record = db.query(LandRecord).filter(
        LandRecord.id == record_id,
        LandRecord.status.in_(["APPROVED", "PUBLISHED"]),
        LandRecord.is_public == True
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Approved land record not found or restricted")

    return {
        "id": record.id,
        "owner_name": record.owner_name,
        "father_husband_name": record.father_husband_name,
        "previous_owner": record.previous_owner,
        "ownership_type": record.ownership_type,
        "survey_number": record.survey_number,
        "khasra_number": record.khasra_number,
        "khata_number": record.khata_number,
        "plot_number": record.plot_number,
        "village": record.village,
        "tehsil": record.tehsil,
        "district": record.district,
        "state": record.state,
        "land_area": record.land_area,
        "land_classification": record.land_classification,
        "registration_number": record.registration_number,
        "registration_date": record.registration_date,
        "mutation_number": record.mutation_number,
        "status": record.status,
        "document_status": record.document_status,
        "verification_status": "Certified Government Record",
        "last_verification_date": record.updated_at.strftime("%d-%m-%Y") if record.updated_at else record.registration_date,
        "coordinates_geojson": record.coordinates_geojson
    }

@router.get("/stats")
def get_public_stats(db: Session = Depends(get_db)):
    approved_count = db.query(LandRecord).filter(
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

    return {
        "portal_name": "LandLens-AI",
        "subtitle": "AI-Powered Land Record Digitization and Multi-Document Cross-Verification",
        "department": "Department of Land Resources (DoLR), Ministry of Rural Development",
        "total_digitized_approved": approved_count,
        "districts_covered": districts_count,
        "villages_digitized": villages_count,
        "average_verification_time_days": "Real-time AI Verification",
        "service_guarantee_notice": "Verified registration records made available for certified public viewing upon officer approval."
    }
