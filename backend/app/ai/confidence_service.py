from typing import Dict, Any
from backend.app.ai.multilingual.confidence_service import ConfidenceScoringService

class ConfidenceService:
    """
    Standardized field-level confidence service.
    Tiers:
    - 90–100% = HIGH
    - 80–89% = MEDIUM
    - Below 80% = LOW (requires_review = true)
    """

    @staticmethod
    def get_tier(confidence: float) -> str:
        if confidence >= 90.0:
            return "HIGH"
        elif confidence >= 80.0:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def evaluate_field_confidences(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        eval_res = ConfidenceScoringService.evaluate_record(extracted_data)
        fevals = eval_res["field_evaluations"]

        fields_dict = {}
        for k, v in extracted_data.items():
            f_eval = fevals.get(k, {})
            conf = f_eval.get("confidence", 90.0 if v else 45.0)
            tier = f_eval.get("tier", ConfidenceService.get_tier(conf))
            requires_review = f_eval.get("requires_review", conf < 80.0)

            fields_dict[k] = {
                "value": v,
                "confidence": conf,
                "tier": tier,
                "requires_review": requires_review
            }

        return {
            "fields": fields_dict,
            "average_confidence": eval_res["average_confidence"],
            "overall_tier": eval_res["overall_tier"],
            "is_high_quality": eval_res["average_confidence"] >= 80.0,
            "requires_human_verification": eval_res["requires_human_verification"]
        }
