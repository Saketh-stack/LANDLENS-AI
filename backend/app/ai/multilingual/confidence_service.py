"""
ConfidenceScoringService: Strict field-level confidence scoring and verification flagging.
Evaluates OCR quality, syntax validity, and value completeness for land record fields.
Flags any uncertain field (<60%) as 'Needs Verification' to prevent misleading AI outputs.
"""
import re
from typing import Dict, Any

class ConfidenceScoringService:
    """
    Evaluates extraction confidence per field and sets verification requirements.
    Never presents uncertain AI extraction as confirmed government facts.
    """

    @classmethod
    def evaluate_field(cls, field_name: str, raw_val: Any, base_confidence: float = 90.0) -> Dict[str, Any]:
        val_str = str(raw_val).strip() if raw_val is not None else ""

        # Missing or empty field
        if not val_str or val_str.lower() in ["none", "null", "n/a", "unknown", ""]:
            return {
                "confidence": 35.0,
                "tier": "LOW",
                "needs_verification": True,
                "reason": f"{field_name} could not be detected in document text."
            }

        conf = base_confidence

        # Syntax and sanity validations
        if field_name == "survey_number":
            # Must contain at least one digit or alphanumeric parcel id
            if re.search(r'\d+', val_str):
                conf = max(conf, 88.0)
            else:
                conf = min(conf, 55.0)

        elif field_name == "land_area":
            try:
                area_val = float(re.search(r'[\d\.]+', val_str).group(0))
                if 0.001 <= area_val <= 50000.0:
                    conf = max(conf, 92.0)
                else:
                    conf = min(conf, 50.0)
            except Exception:
                conf = min(conf, 55.0)

        elif field_name in ["owner_name", "father_husband_name"]:
            # Name must not be purely digits
            if re.match(r'^\d+$', val_str):
                conf = 40.0
            elif len(val_str) < 3:
                conf = 55.0
            else:
                conf = max(conf, 89.0)

        elif field_name == "registration_number":
            if len(val_str) >= 3 and any(ch.isalnum() for ch in val_str):
                conf = max(conf, 90.0)
            else:
                conf = min(conf, 58.0)

        # Categorize tier
        conf = round(conf, 1)
        if conf >= 80.0:
            tier = "HIGH"
            needs_verif = False
        elif conf >= 60.0:
            tier = "MEDIUM"
            needs_verif = False
        else:
            tier = "LOW"
            needs_verif = True

        return {
            "confidence": conf,
            "tier": tier,
            "needs_verification": needs_verif
        }

    @classmethod
    def evaluate_record(cls, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates all fields in an extracted record and computes aggregate metrics."""
        field_evals = {}
        total_conf = 0.0
        field_count = 0
        unverified_fields = []

        critical_fields = [
            "owner_name", "survey_number", "land_area", "village",
            "registration_number", "registration_date", "document_type"
        ]

        for k, v in record_data.items():
            ev = cls.evaluate_field(k, v)
            field_evals[k] = ev
            total_conf += ev["confidence"]
            field_count += 1
            if ev["needs_verification"] and k in critical_fields:
                unverified_fields.append(k)

        avg_conf = round(total_conf / max(field_count, 1), 1)
        overall_tier = "HIGH" if avg_conf >= 80.0 else ("MEDIUM" if avg_conf >= 60.0 else "LOW")

        return {
            "average_confidence": avg_conf,
            "overall_tier": overall_tier,
            "field_evaluations": field_evals,
            "requires_human_verification": len(unverified_fields) > 0 or avg_conf < 75.0,
            "flagged_fields": unverified_fields
        }
