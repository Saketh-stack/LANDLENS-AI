from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.land_record import LandRecord

class SearchService:
    @staticmethod
    def search_all_records(
        query_str: str,
        db: Session,
        include_internal: bool = False
    ) -> List[LandRecord]:
        q = db.query(LandRecord)
        if not include_internal:
            q = q.filter(LandRecord.is_public == True, LandRecord.status.in_(["APPROVED", "PUBLISHED"]))

        kw = f"%{query_str.strip()}%"
        q = q.filter(
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
        return q.all()
