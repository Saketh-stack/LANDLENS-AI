"""
TextNormalizationService: Normalizes Indic numerals, land measurement units, and dates
into standardized canonical values while strictly preserving the original raw representations.
"""
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Master Indian Numeral Translation Table
ALL_INDIC_DIGIT_MAP = {
    # Devanagari (Hindi, Marathi)
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    # Telugu
    '౦': '0', '౧': '1', '౨': '2', '౩': '3', '౪': '4', '౫': '5', '౬': '6', '౭': '7', '౮': '8', '౯': '9',
    # Tamil
    '௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4', '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9',
    # Bengali / Assamese
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
    # Gujarati
    '૦': '0', '૧': '1', '૨': '2', '૩': '3', '૪': '4', '૫': '5', '૬': '6', '૭': '7', '૮': '8', '૯': '9',
    # Gurmukhi (Punjabi)
    '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4', '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9',
    # Odia
    '୦': '0', '୧': '1', '୨': '2', '୩': '3', '୪': '4', '୫': '5', '୬': '6', '୭': '7', '୮': '8', '୯': '9',
    # Kannada
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4', '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9',
    # Malayalam
    '൦': '0', '൧': '1', '൨': '2', '൩': '3', '൪': '4', '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9',
    # Urdu / Perso-Arabic
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
}

TRANSLATION_TABLE = str.maketrans(ALL_INDIC_DIGIT_MAP)

class TextNormalizationService:
    """
    Normalizes numbers, dates, and land units while preserving original strings.
    """

    @classmethod
    def normalize_numerals(cls, text: str) -> str:
        """Converts any Indic script numeral in the text to standard ASCII 0-9."""
        if not text:
            return ""
        return text.translate(TRANSLATION_TABLE)

    @classmethod
    def normalize_land_area(cls, raw_area: Any) -> Dict[str, Any]:
        """
        Normalizes area strings or numbers (Acres, Guntas, Bigha, Cent, etc.)
        into float acres while preserving raw original value and unit.
        """
        if raw_area is None or raw_area == "":
            return {"original": "", "normalized_acres": None, "unit": "Unknown", "formatted": "N/A"}

        orig_str = str(raw_area).strip()
        # Convert any Indic numerals in the string first
        ascii_str = cls.normalize_numerals(orig_str).lower()

        # Multipliers to standard Acre
        UNIT_FACTORS = [
            (r'(?:guntha|gunta|गुंठा|గుంటలు|గుంట|ಗುಂಟೆ)s?', 0.025, "Guntas"),
            (r'(?:cent|cents|சென்ட்|സെന്റ്)s?', 0.01, "Cents"),
            (r'(?:ground|grounds|கிரவுண்ட்)s?', 0.055, "Grounds"),
            (r'(?:bigha|बीघा|বিঘা|વીઘા|বীঘা)s?', 0.625, "Bigha"),
            (r'(?:biswa|बिस्वा|ਬਿਸਵਾ)s?', 0.03125, "Biswa"),
            (r'(?:hectare|हेक्टेयर|ஹெக்டேர்|హెక్టార్లు|ಹೆಕ್ಟೇರ್)s?', 2.47105, "Hectares"),
            (r'(?:are|ares|आर)s?', 0.02471, "Ares"),
            (r'(?:kanal|कनाल|ਕਨਾਲ)s?', 0.125, "Kanal"),
            (r'(?:marla|मरला|ਮਰਲਾ)s?', 0.00625, "Marla"),
            (r'(?:sq(?:uare)?\s*(?:yd|yard|gaj|गज|వారాలు))', 0.0002066, "Sq Yards"),
            (r'(?:acre|acres|एकड़|ఏకరాలు|ഏക്കർ|ಎಕರೆ)s?', 1.0, "Acres")
        ]

        for pat, factor, unit_name in UNIT_FACTORS:
            match = re.search(r'([\d\.]+)\s*' + pat, ascii_str)
            if match:
                try:
                    qty = float(match.group(1))
                    normalized = round(qty * factor, 4)
                    return {
                        "original": orig_str,
                        "normalized_acres": normalized,
                        "unit": unit_name,
                        "formatted": f"{normalized:.2f} Acres ({orig_str})"
                    }
                except ValueError:
                    pass

        # If pure number without explicit unit, assume Acres
        pure_num = re.search(r'[\d\.]+', ascii_str)
        if pure_num:
            try:
                val = float(pure_num.group(0))
                return {
                    "original": orig_str,
                    "normalized_acres": round(val, 4),
                    "unit": "Acres",
                    "formatted": f"{val:.2f} Acres"
                }
            except ValueError:
                pass

        return {
            "original": orig_str,
            "normalized_acres": None,
            "unit": "Unspecified",
            "formatted": orig_str
        }

    @classmethod
    def normalize_date(cls, raw_date: Any) -> Dict[str, Any]:
        """
        Parses multiple Indian date formats (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
        and outputs standardized ISO YYYY-MM-DD alongside original representation.
        """
        if not raw_date:
            return {"original": "", "normalized_iso": None, "formatted": "N/A"}

        orig_str = str(raw_date).strip()
        ascii_str = cls.normalize_numerals(orig_str)

        date_patterns = [
            (r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})', "%d/%m/%Y"),
            (r'(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})', "%Y/%m/%d"),
            (r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', "%d %B %Y")
        ]

        clean_dt = re.sub(r'[\-\.]', '/', ascii_str)
        for pat, fmt in [
            (r'^(\d{1,2})\/(\d{1,2})\/(\d{4})$', "%d/%m/%Y"),
            (r'^(\d{4})\/(\d{1,2})\/(\d{1,2})$', "%Y/%m/%d"),
        ]:
            m = re.match(pat, clean_dt)
            if m:
                try:
                    dt = datetime.strptime(clean_dt, fmt)
                    iso = dt.strftime("%Y-%m-%d")
                    return {
                        "original": orig_str,
                        "normalized_iso": iso,
                        "formatted": dt.strftime("%d-%b-%Y")
                    }
                except ValueError:
                    pass

        return {
            "original": orig_str,
            "normalized_iso": None,
            "formatted": orig_str
        }

    @classmethod
    def normalize_survey_number(cls, raw_survey: Any) -> Dict[str, Any]:
        """
        Normalizes survey numbers by converting Indic digits, stripping whitespace,
        and standardizing slashes (e.g. '184 / A' -> '184/A').
        """
        if not raw_survey:
            return {"original": "", "normalized": "", "formatted": "N/A"}

        orig_str = str(raw_survey).strip()
        ascii_str = cls.normalize_numerals(orig_str)
        # Clean internal spaces around slashes or hyphens
        normalized = re.sub(r'\s*([/\-\_])\s*', r'\1', ascii_str).upper()

        return {
            "original": orig_str,
            "normalized": normalized,
            "formatted": normalized
        }
