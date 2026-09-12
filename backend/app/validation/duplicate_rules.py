from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.land_record import LandRecord

class DuplicateRulesEngine:
    @classmethod
    def check_parcel_collision(
        cls,
        survey_number: str,
        village: str,
        district: str,
        current_record_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        if not db or not survey_number:
            return {"is_duplicate": False, "conflicts": []}

        query = db.query(LandRecord).filter(
            LandRecord.survey_number == survey_number,
            LandRecord.village.ilike(village),
            LandRecord.district.ilike(district)
        )
        if current_record_id:
            query = query.filter(LandRecord.id != current_record_id)

        conflicts = query.all()
        return {
            "is_duplicate": len(conflicts) > 0,
            "count": len(conflicts),
            "conflicts": [
                {
                    "id": c.id,
                    "owner_name": c.owner_name,
                    "registration_number": c.registration_number,
                    "status": c.status
                }
                for c in conflicts
            ]
        }
