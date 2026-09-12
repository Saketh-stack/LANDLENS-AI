"""
TranslationService: Translates descriptive administrative clauses and deed terms
between Indian languages and English.
Includes mandatory legal disclaimer preserving legal factuality in original script.
"""
from typing import Dict, Any, Optional

DEED_TYPE_TRANSLATIONS = {
    "క్రయవిక్రయ పత్రము": "Sale Deed (Conveyance)",
    "క్రయ దస్తావేజు": "Sale Deed",
    "దాన పత్రం": "Gift Deed",
    "విభజన పత్రం": "Partition Deed",
    "భాగ పరిష్కార పత్రం": "Family Settlement Deed",
    "విక్రయ పత్ర": "Sale Deed",
    "बैनामा": "Sale Deed",
    "विक्रय पत्र": "Sale Deed",
    "दान पत्र": "Gift Deed",
    "हक त्याग पत्र": "Relinquishment Deed",
    "खरेदीखत": "Sale Deed",
    "दानपत्र": "Gift Deed",
    "हक्कसोडपत्र": "Relinquishment Deed",
    "கிரய பத்திரம்": "Sale Deed",
    "தான பத்திரம்": "Gift Deed",
    "பாகப்பிரிவினை": "Partition Deed",
    "ಕ್ರಯ ಪತ್ರ": "Sale Deed",
    "ದಾನ ಪತ್ರ": "Gift Deed",
    "തീറാധാരം": "Sale Deed",
    "ദാനധാരം": "Gift Deed",
    "বিক্রয় দলিল": "Sale Deed",
    "দানপত্র": "Gift Deed",
    "ਬੈਨਾਮਾ": "Sale Deed",
    "ਬਿਕਰੀ ਦਸਤਾਵੇਜ਼": "Sale Deed",
    "ବିକ୍ରୟ ଦଲିଲ": "Sale Deed",
    "বিক্ৰী দলিল": "Sale Deed",
    "بیع نامہ": "Sale Deed",
    "ہبہ نامہ": "Gift Deed"
}

CLASSIFICATION_TRANSLATIONS = {
    "వ్యవసాయ భూమి": "Agricultural Land",
    "మాగాణి": "Wet / Irrigated Agricultural Land",
    "మెట్ట": "Dry Agricultural Land",
    "ఇళ్ల స్థలం": "Residential Plot",
    "कृषि भूमि": "Agricultural Land",
    "आवासीय": "Residential Land",
    "व्यावसायिक": "Commercial Land",
    "बंजर": "Barren / Wasteland",
    "शेतजमीन": "Agricultural Farmland",
    "जिरायत": "Dry Farming Land",
    "बागायत": "Orchard / Irrigated Land",
    "விவசாய நிலம்": "Agricultural Land",
    "நன்செய்": "Wet Farming Land",
    "புன்செய்": "Dry Farming Land",
    "மனை": "Residential House Site",
    "ತರಿ": "Wet Land",
    "ಖುಷ್ಕಿ": "Dry Land",
    "തരം നിലം": "Agricultural Land",
    "കരഭൂമി": "Dry Upland",
    "কৃষি জমি": "Agricultural Land",
    "বাস্তু": "Homestead / Residential Land",
    "زرعی زمین": "Agricultural Land",
    "رہائشی": "Residential Land"
}

LEGAL_DISCLAIMER = (
    "LEGAL FACTUALITY NOTICE: English translations are rendered for public and administrative "
    "readability only. Under the Registration Act 1908 and State Land Revenue Codes, official legal validity "
    "and certified ownership boundaries reside strictly in the original registered document and script."
)

class TranslationService:
    """
    Translates non-name legal terms and clauses to English while maintaining legal disclaimers.
    """

    @classmethod
    def translate_legal_term(cls, term: str) -> Dict[str, Any]:
        if not term:
            return {"original": "", "translated": "", "confidence": 100.0, "disclaimer": LEGAL_DISCLAIMER}

        clean = term.strip()

        # Check deed type
        if clean in DEED_TYPE_TRANSLATIONS:
            return {
                "original": clean,
                "translated": DEED_TYPE_TRANSLATIONS[clean],
                "confidence": 99.0,
                "disclaimer": LEGAL_DISCLAIMER
            }

        # Check land classification
        if clean in CLASSIFICATION_TRANSLATIONS:
            return {
                "original": clean,
                "translated": CLASSIFICATION_TRANSLATIONS[clean],
                "confidence": 99.0,
                "disclaimer": LEGAL_DISCLAIMER
            }

        # Check substring match
        for k, v in {**DEED_TYPE_TRANSLATIONS, **CLASSIFICATION_TRANSLATIONS}.items():
            if k in clean:
                return {
                    "original": clean,
                    "translated": v,
                    "confidence": 90.0,
                    "disclaimer": LEGAL_DISCLAIMER
                }

        return {
            "original": clean,
            "translated": clean,
            "confidence": 75.0,
            "disclaimer": LEGAL_DISCLAIMER,
            "needs_human_verification": True
        }
