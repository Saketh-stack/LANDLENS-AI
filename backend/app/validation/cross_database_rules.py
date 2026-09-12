from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.cadastral_record import CadastralRecord

class CrossDatabaseRulesEngine:
    @classmethod
    def reconcile_cadastral_ground_truth(
        cls,
        survey_number: str,
        deed_area: float,
        village: str,
        district: str,
        db: Session
    ) -> Dict[str, Any]:
        cad = db.query(CadastralRecord).filter(
            CadastralRecord.survey_number == survey_number
        ).first()

        if not cad:
            return {
                "matched": False,
                "message": f"No baseline cadastral ground-truth entry found for survey number {survey_number}.",
                "has_discrepancy": False
            }

        delta = abs(deed_area - cad.cadastral_area)
        has_discrepancy = delta > 0.01

        return {
            "matched": True,
            "cadastral_id": cad.id,
            "survey_number": cad.survey_number,
            "cadastral_area": cad.cadastral_area,
            "deed_area": deed_area,
            "delta": round(delta, 3),
            "has_discrepancy": has_discrepancy,
            "recommended_action": "SYNC_TO_CADASTRAL" if has_discrepancy else "CONFIRMED",
            "message": (
                f"Area mismatch detected: Land Deed = {deed_area} Acres, Cadastral Ground Truth = {cad.cadastral_area} Acres."
                if has_discrepancy
                else "Land area matches official Cadastral Ground Truth."
            )
        }
