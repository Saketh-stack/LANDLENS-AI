from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.cadastral_record import CadastralRecord

class CadastralSystemAdapter:
    @classmethod
    def get_parcel_by_survey_no(cls, survey_number: str, db: Session) -> Optional[CadastralRecord]:
        return db.query(CadastralRecord).filter(CadastralRecord.survey_number == survey_number).first()

    @classmethod
    def list_parcels(cls, village: Optional[str] = None, district: Optional[str] = None, db: Optional[Session] = None) -> List[CadastralRecord]:
        if not db:
            return []
        query = db.query(CadastralRecord)
        if village:
            query = query.filter(CadastralRecord.village.ilike(village))
        if district:
            query = query.filter(CadastralRecord.district.ilike(district))
        return query.all()
