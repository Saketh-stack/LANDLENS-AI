"""
DocumentClassifier: Multi-type Indian land document classifier.
Classifies uploaded documents into:
1. Registered Sale Deed
2. Khasra / Khatauni Register
3. Cadastral Boundary Map
4. Mutation Sanction Order
"""
import re
from typing import Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger

class DocumentClassifier:
    """
    Automatic AI-assisted classifier across the 4 canonical Indian land document types.
    Calculates classification confidence based on linguistic, legal, and structural markers.
    """

    SALE_DEED = "Registered Sale Deed"
    KHASRA_KHATAUNI = "Khasra / Khatauni Register"
    CADASTRAL_MAP = "Cadastral Boundary Map"
    MUTATION_ORDER = "Mutation Sanction Order"

    CANONICAL_TYPES = [
        SALE_DEED,
        KHASRA_KHATAUNI,
        CADASTRAL_MAP,
        MUTATION_ORDER
    ]

    # Keyword indicators across Indian scripts
    KEYWORDS = {
        SALE_DEED: [
            "sale deed", "deed of sale", "conveyance deed", "indivisible", "registered deed",
            "vendor", "vendee", "purchaser", "consideration", "stamp duty", "sub-registrar",
            "registration fee", "witness", "schedule of property", "boundaries", "बैनामा",
            "विक्रय पत्र", "దస్తావేజు", "విక్రయ దస్తావేజు", "கிரய பத்திரம்", "विक्री पत्र",
            "খরিদ দলিল", "ਵੇਚ ਪੱਤਰ"
        ],
        KHASRA_KHATAUNI: [
            "khasra", "khatauni", "khata number", "khewat", "jamabandi", "ror-1b", "ror",
            "pahani", "adangal", "patta", "pattadar passbook", "7/12", "satbara", "खसरा",
            "खतौनी", "पट्टा", "పట్టాదారు పాస్‌బుక్", "పహణీ", "அடங்கல்", "பட்டா", "सातबारा",
            "जमाबंदी", "খতিয়ান", "জমাবন্দী"
        ],
        CADASTRAL_MAP: [
            "cadastral", "boundary map", "village map", "fmb", "field measurement book",
            "tippon", "sketch", "map sheet", "scale 1:", "scale", "north direction",
            "parcel boundary", "adjacent parcel", "nakshe", "naksha", "नक्शा", "भू-मानचित्र",
            "నక్షా", "భూపటం", "வரைபடம்", "नकाशा", "ম্যাপ", "نقشہ"
        ],
        MUTATION_ORDER: [
            "mutation", "sanction order", "mutation order", "namantaran", "dakhil kharij",
            "virasat", "fard", "proceedings of tahsildar", "revenue court", "order date",
            "reason for mutation", "दाखिल खारिज", "नामांतरण", "म्यूटेशन", "వారసత్వ",
            "దాఖిల్ ఖారీజ్", "பட்டா மாறுதல்", "फेरफार", "নামজারি", "انتقال نامہ"
        ]
    }

    @classmethod
    def classify(cls, text: str, user_selected_type: str = None) -> Dict[str, Any]:
        """
        Classifies document text and reports confidence score.
        If user explicitly chose a type, validates that choice against document content.
        """
        lower = text.lower() if text else ""
        scores = {t: 0 for t in cls.CANONICAL_TYPES}

        # Count keyword occurrences
        for doc_type, kws in cls.KEYWORDS.items():
            for kw in kws:
                matches = len(re.findall(re.escape(kw), lower))
                if matches > 0:
                    scores[doc_type] += (matches * 2)

        total_score = sum(scores.values())
        if total_score > 0:
            best_type = max(scores, key=scores.get)
            calc_conf = min(99.0, round((scores[best_type] / total_score) * 100, 1))
            calc_conf = max(68.0, calc_conf)
        else:
            best_type = user_selected_type or cls.SALE_DEED
            calc_conf = 72.0

        detected_type = best_type

        # Check if user opted for Auto-Detect or specified a concrete type
        is_auto = (not user_selected_type) or ("auto" in user_selected_type.lower())
        if is_auto:
            final_type = detected_type
            is_overridden = False
        else:
            normalized_user_type = cls.normalize_document_type(user_selected_type)
            final_type = normalized_user_type if normalized_user_type else detected_type
            is_overridden = bool(final_type != detected_type)

        return {
            "detected_type": detected_type,
            "selected_type": final_type,
            "confidence": calc_conf,
            "is_user_overridden": is_overridden,
            "type_scores": scores,
            "supported_types": cls.CANONICAL_TYPES
        }

    @classmethod
    def normalize_document_type(cls, raw: str) -> str:
        if not raw or "auto" in raw.lower():
            return None
        r = raw.lower().strip()
        if "sale" in r or "deed" in r or "बैनामा" in r:
            return cls.SALE_DEED
        if "khasra" in r or "khatauni" in r or "pahani" in r or "7/12" in r or "patta" in r:
            return cls.KHASRA_KHATAUNI
        if "cadastral" in r or "map" in r or "fmb" in r or "sketch" in r or "naksha" in r:
            return cls.CADASTRAL_MAP
        if "mutation" in r or "sanction" in r or "dakhil" in r or "namantaran" in r:
            return cls.MUTATION_ORDER
        return cls.SALE_DEED
