from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.validation.duplicate_rules import DuplicateRulesEngine

class DuplicateService:
    @staticmethod
    def check_duplicate(
        survey_number: str,
        village: str,
        district: str,
        record_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        return DuplicateRulesEngine.check_parcel_collision(
            survey_number=survey_number,
            village=village,
            district=district,
            current_record_id=record_id,
            db=db
        )
