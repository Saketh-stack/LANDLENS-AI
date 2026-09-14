"""
ConfidenceScoringService: Strict field-level confidence scoring and review flagging.
Evaluates OCR quality, syntax validity, value completeness, and numerical ambiguity.
Enforces the government standard:
- 90–100% = HIGH
- 80–89% = MEDIUM
- Below 80% = LOW (requires_review = true)
"""
import re
from typing import Dict, Any, Optional
from backend.app.ai.multilingual.number_analyzer import NumberAnalyzer

class ConfidenceScoringService:
    """
    Evaluates extraction confidence per field and sets verification requirements.
    Never presents uncertain AI extraction as confirmed government facts.
    """

    @classmethod
    def evaluate_field(cls, field_name: str, raw_val: Any, base_confidence: float = 95.0) -> Dict[str, Any]:
        val_str = str(raw_val).strip() if raw_val is not None else ""

        # Missing, empty, or unparseable field
        if not val_str or val_str.lower() in ["none", "null", "n/a", "unknown", "", "not found", "?", "???", "..."] or not re.search(r'[A-Za-z0-9\u0900-\u0D7F]', val_str):
            return {
                "confidence": 40.0,
                "tier": "LOW",
                "requires_review": True,
                "needs_verification": True,
                "reason": f"{field_name} could not be detected in document text."
            }

        # Check for number ambiguities via NumberAnalyzer
        num_res = NumberAnalyzer.analyze(field_name, val_str, base_confidence)
        if num_res["ambiguity_detected"]:
            return {
                "confidence": num_res["confidence"],
                "tier": "LOW",
                "requires_review": True,
                "needs_verification": True,
                "reason": num_res["reason"],
                "possible_alternatives": num_res["possible_alternatives"]
            }

        conf = base_confidence

        # Syntax and sanity validations
        if field_name == "survey_number":
            # Must contain at least one digit or alphanumeric parcel id (e.g. 184/A, 123/4A, 45/1)
            if re.match(r'^[0-9]+(/[A-Za-z0-9]+)?$', val_str) or re.match(r'^[0-9]+[A-Za-z]*$', val_str):
                conf = max(conf, 94.0)
            elif re.search(r'\d+', val_str):
                conf = 85.0
            else:
                conf = 60.0

        elif field_name == "land_area":
            try:
                area_match = re.search(r'[\d\.]+', val_str)
                if area_match:
                    area_val = float(area_match.group(0))
                    if 0.01 <= area_val <= 5000.0:
                        conf = max(conf, 92.0)
                    else:
                        conf = 65.0
                else:
                    conf = 55.0
            except Exception:
                conf = 55.0

        elif field_name in ["owner_name", "father_husband_name", "previous_owner", "current_owner"]:
            # Name must not be purely digits
            if re.match(r'^\d+$', val_str):
                conf = 45.0
            elif len(val_str) < 3:
                conf = 60.0
            else:
                conf = max(conf, 93.0)

        elif field_name in ["village", "tehsil", "taluk", "mandal", "district", "state"]:
            if len(val_str) >= 2 and not re.match(r'^\d+$', val_str):
                conf = max(conf, 92.0)
            else:
                conf = 65.0

        elif field_name == "registration_number":
            if len(val_str) >= 4 and any(ch.isalnum() for ch in val_str):
                conf = max(conf, 94.0)
            else:
                conf = 65.0

        elif field_name == "registration_date":
            # Check for date pattern
            if re.search(r'\d{1,4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,4}', val_str):
                conf = max(conf, 93.0)
            else:
                conf = 70.0

        # Enforce exact statutory tiers:
        # 90-100% = HIGH
        # 80-89% = MEDIUM
        # Below 80% = LOW (requires_review = true)
        conf = round(min(99.0, max(10.0, conf)), 1)
        if conf >= 90.0:
            tier = "HIGH"
            requires_review = False
        elif conf >= 80.0:
            tier = "MEDIUM"
            requires_review = False
        else:
            tier = "LOW"
            requires_review = True

        return {
            "confidence": conf,
            "tier": tier,
            "requires_review": requires_review,
            "needs_verification": requires_review
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
            is_present = v is not None and str(v).strip() not in ["", "None", "null", "Not found", "N/A", "?"]
            if is_present:
                total_conf += ev["confidence"]
                field_count += 1
            elif k in critical_fields:
                # Missing mandatory/critical field incurs low confidence score in document average
                total_conf += ev["confidence"]
                field_count += 1

            if ev["requires_review"] and k in critical_fields:
                unverified_fields.append(k)

        avg_conf = round(total_conf / max(field_count, 1), 1) if field_count > 0 else 40.0
        overall_tier = "HIGH" if avg_conf >= 90.0 else ("MEDIUM" if avg_conf >= 80.0 else "LOW")

        return {
            "average_confidence": avg_conf,
            "overall_tier": overall_tier,
            "field_evaluations": field_evals,
            "requires_human_verification": len(unverified_fields) > 0 or avg_conf < 80.0,
            "flagged_fields": unverified_fields
        }
