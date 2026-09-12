from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.validation.rules import BusinessRulesEngine
from backend.app.models.validation_result import ValidationResult

class ValidationService:
    @staticmethod
    def validate_record_data(
        record_data: Dict[str, Any],
        db: Session,
        land_record_id: Optional[int] = None,
        registration_id: Optional[int] = None,
        persist: bool = False
    ) -> Dict[str, Any]:
        val_summary = BusinessRulesEngine.validate_all(record_data, db=db)

        if persist and (land_record_id or registration_id):
            # Clean old results
            if land_record_id:
                db.query(ValidationResult).filter(ValidationResult.land_record_id == land_record_id).delete()
            if registration_id:
                db.query(ValidationResult).filter(ValidationResult.registration_id == registration_id).delete()

            for r in val_summary["results"]:
                res = ValidationResult(
                    land_record_id=land_record_id,
                    registration_id=registration_id,
                    rule_id=r["rule_id"],
                    rule_name=r["rule_name"],
                    status=r["status"],
                    message=r["message"],
                    details=r.get("details")
                )
                db.add(res)
            db.commit()

        return val_summary
