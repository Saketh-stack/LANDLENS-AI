from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.land_record import LandRecord
from backend.app.schemas.land_record import LandRecordCreate, LandRecordUpdate

class LandRecordService:
    @staticmethod
    def get_public_records(
        db: Session,
        q: Optional[str] = None,
        owner_name: Optional[str] = None,
        survey_number: Optional[str] = None,
        khasra_number: Optional[str] = None,
        khata_number: Optional[str] = None,
        village: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 50
    ) -> List[LandRecord]:
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
        if village:
            query = query.filter(LandRecord.village.ilike(f"%{village.strip()}%"))
        if district:
            query = query.filter(LandRecord.district.ilike(f"%{district.strip()}%"))

        return query.order_by(LandRecord.id.desc()).limit(limit).all()

    @staticmethod
    def get_record_by_id(record_id: int, db: Session) -> Optional[LandRecord]:
        return db.query(LandRecord).filter(LandRecord.id == record_id).first()

    @staticmethod
    def create_record(data: LandRecordCreate, db: Session) -> LandRecord:
        record = LandRecord(**data.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_record(record_id: int, data: LandRecordUpdate, db: Session) -> Optional[LandRecord]:
        record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
        if not record:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(record, k, v)
        db.commit()
        db.refresh(record)
        return record
