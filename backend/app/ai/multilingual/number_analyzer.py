"""
NumberAnalyzer: High-precision number ambiguity detector for Indian land records.
Analyzes Survey numbers, Khasra numbers, Khata numbers, Registration numbers, and Areas
for critical OCR optical confusions (0/O, 1/I/l, 2/Z, 5/S, 6/G, 8/B).
Crucial rule: Never silently alter uncertain characters. Flag for officer review.
"""
import re
from typing import Dict, Any, List, Optional

class NumberAnalyzer:
    """
    Analyzes numerical and alphanumeric land record entities for character ambiguities.
    """

    CONFUSION_MAP = {
        'Z': {'digit': '2', 'char_desc': "uppercase 'Z' vs digit '2'"},
        'O': {'digit': '0', 'char_desc': "uppercase letter 'O' vs digit '0'"},
        'o': {'digit': '0', 'char_desc': "lowercase letter 'o' vs digit '0'"},
        'I': {'digit': '1', 'char_desc': "uppercase letter 'I' vs digit '1'"},
        'l': {'digit': '1', 'char_desc': "lowercase letter 'l' vs digit '1'"},
        'S': {'digit': '5', 'char_desc': "uppercase letter 'S' vs digit '5'"},
        's': {'digit': '5', 'char_desc': "lowercase letter 's' vs digit '5'"},
        'G': {'digit': '6', 'char_desc': "uppercase letter 'G' vs digit '6'"},
        'B': {'digit': '8', 'char_desc': "uppercase letter 'B' vs digit '8'"}
    }

    @classmethod
    def analyze(cls, field_name: str, value: Any, base_confidence: float = 95.0) -> Dict[str, Any]:
        """
        Inspects field value for optical character ambiguities.
        Returns:
            {
                "value": str,
                "confidence": float,
                "requires_review": bool,
                "ambiguity_detected": bool,
                "reason": Optional[str],
                "possible_alternatives": List[str]
            }
        """
        if value is None or str(value).strip().lower() in ["", "none", "null", "not found"]:
            return {
                "value": "Not found",
                "confidence": 40.0,
                "requires_review": True,
                "ambiguity_detected": False,
                "reason": "Missing value",
                "possible_alternatives": []
            }

        str_val = str(value).strip()
        f_type = field_name.lower()

        # Check for Survey / Khasra / Plot number ambiguity
        if any(k in f_type for k in ["survey", "khasra", "khata", "plot", "sub_division"]):
            return cls._check_survey_number(str_val, base_confidence)

        # Check for Land Area numeric ambiguity
        if any(k in f_type for k in ["area", "extent"]):
            return cls._check_area_number(str_val, base_confidence)

        # Check for Registration / Mutation / Document number
        if any(k in f_type for k in ["registration_number", "mutation_number", "document_number"]):
            return cls._check_registration_number(str_val, base_confidence)

        # General text / name field
        return {
            "value": str_val,
            "confidence": round(base_confidence, 1),
            "requires_review": bool(base_confidence < 80.0),
            "ambiguity_detected": False,
            "reason": None,
            "possible_alternatives": []
        }

    @classmethod
    def _check_survey_number(cls, val: str, base_conf: float) -> Dict[str, Any]:
        """
        Checks survey number notations like 125/2, 125-2, 125/Z, 125/4B, 184/A.
        Identifies if subdivision or number has suspected letter/digit confusions like 125/Z.
        """
        # Detect slash pattern: e.g. 125/Z or 125/2 or 101-B
        slash_match = re.search(r'^(\d+)\s*[\/\-]\s*([A-Za-z0-9]+)$', val)
        if slash_match:
            main_num, sub_num = slash_match.group(1), slash_match.group(2)

            # Check if sub_num has single letter Z, O, I, S, B that might be a digit
            # e.g. 125/Z is strongly suspected to be 125/2
            if sub_num in ['Z', 'z']:
                alt = f"{main_num}/2"
                return {
                    "value": val,  # NEVER silently change uncertain characters!
                    "confidence": min(61.0, base_conf),
                    "requires_review": True,
                    "ambiguity_detected": True,
                    "reason": "Suspected optical confusion: 'Z' in subdivision notation may represent digit '2' (e.g. 125/2 vs 125/Z)",
                    "possible_alternatives": [alt]
                }
            elif sub_num in ['O', 'o']:
                alt = f"{main_num}/0"
                return {
                    "value": val,
                    "confidence": min(62.0, base_conf),
                    "requires_review": True,
                    "ambiguity_detected": True,
                    "reason": "Suspected optical confusion: letter 'O' in subdivision notation may represent digit '0'",
                    "possible_alternatives": [alt]
                }
            elif sub_num in ['l', 'I'] and len(sub_num) == 1:
                alt = f"{main_num}/1"
                return {
                    "value": val,
                    "confidence": min(65.0, base_conf),
                    "requires_review": True,
                    "ambiguity_detected": True,
                    "reason": "Suspected optical confusion: letter 'I/l' in subdivision notation may represent digit '1'",
                    "possible_alternatives": [alt]
                }

        # Check for letters embedded inside numeric main body, e.g. "12O/4" or "l25/2"
        if re.search(r'\d+[OIlSZGB]\d+', val):
            return {
                "value": val,
                "confidence": min(64.0, base_conf),
                "requires_review": True,
                "ambiguity_detected": True,
                "reason": "Suspected alpha character inside numeric survey digits",
                "possible_alternatives": [cls._suggest_numeric_substitutions(val)]
            }

        # Normal valid survey number format (e.g. 184/A, 123/4A, 101/2, 45B)
        is_clean = bool(re.match(r'^[0-9]+(/[A-Za-z0-9]+)?$', val) or re.match(r'^[0-9]+[A-Za-z]*$', val))
        conf = base_conf if is_clean else min(78.0, base_conf)
        return {
            "value": val,
            "confidence": round(conf, 1),
            "requires_review": bool(conf < 80.0),
            "ambiguity_detected": False,
            "reason": None if is_clean else "Non-standard survey notation format",
            "possible_alternatives": []
        }

    @classmethod
    def _check_area_number(cls, val: str, base_conf: float) -> Dict[str, Any]:
        """
        Checks area representations like 2.00 Acres, 3.85, 2.0O, 3.2O.
        """
        # Check for letter O instead of 0 in decimal e.g. "2.0O" or "2.OO"
        if re.search(r'\d+\.\d*[Oo]+', val) or re.search(r'\d+\.[Oo]+', val):
            clean_sub = re.sub(r'[Oo]', '0', val)
            return {
                "value": val,
                "confidence": min(68.0, base_conf),
                "requires_review": True,
                "ambiguity_detected": True,
                "reason": "Suspected letter 'O' instead of decimal digit '0' in area quantity",
                "possible_alternatives": [clean_sub]
            }

        # Check for valid numeric float extraction
        m = re.search(r'([\d\.]+)', val)
        if not m:
            return {
                "value": val,
                "confidence": 45.0,
                "requires_review": True,
                "ambiguity_detected": True,
                "reason": "Could not parse valid numerical land area quantity",
                "possible_alternatives": []
            }

        try:
            num = float(m.group(1))
            if num <= 0.0 or num > 5000.0:
                return {
                    "value": val,
                    "confidence": 60.0,
                    "requires_review": True,
                    "ambiguity_detected": False,
                    "reason": f"Land area {num} is outside typical feasible holding range (0.01 - 5000 Acres)",
                    "possible_alternatives": []
                }
        except ValueError:
            pass

        return {
            "value": val,
            "confidence": round(base_conf, 1),
            "requires_review": bool(base_conf < 80.0),
            "ambiguity_detected": False,
            "reason": None,
            "possible_alternatives": []
        }

    @classmethod
    def _check_registration_number(cls, val: str, base_conf: float) -> Dict[str, Any]:
        """Checks registration number format like REG2026/00735 or REG-2026-00451."""
        if len(val) < 4:
            return {
                "value": val,
                "confidence": 55.0,
                "requires_review": True,
                "ambiguity_detected": True,
                "reason": "Registration number unusually short",
                "possible_alternatives": []
            }

        return {
            "value": val,
            "confidence": round(base_conf, 1),
            "requires_review": bool(base_conf < 80.0),
            "ambiguity_detected": False,
            "reason": None,
            "possible_alternatives": []
        }

    @classmethod
    def _suggest_numeric_substitutions(cls, text: str) -> str:
        s = text
        for char, info in cls.CONFUSION_MAP.items():
            s = s.replace(char, info['digit'])
        return s
