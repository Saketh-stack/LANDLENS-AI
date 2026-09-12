"""
Multilingual API Routes:
Exposes language metadata, script detection, text normalization, and language accuracy telemetry.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.app.ai.multilingual.languages import LanguageConfiguration
from backend.app.ai.multilingual.language_detector import LanguageDetectionService
from backend.app.ai.multilingual.normalizer import TextNormalizationService
from backend.app.ai.multilingual.verification_service import HumanVerificationService

router = APIRouter(prefix="/api/multilingual", tags=["Multilingual Recognition"])

class DetectRequest(BaseModel):
    text: str

class NormalizeRequest(BaseModel):
    text: str

@router.get("/languages")
def get_supported_languages() -> List[Dict[str, Any]]:
    """Returns metadata for all 13 supported Indian languages."""
    langs = LanguageConfiguration.get_all_languages()
    res = []
    for code, meta in langs.items():
        res.append({
            "code": meta.code,
            "name": meta.name,
            "native_name": meta.native_name,
            "script": meta.script,
            "locale_code": meta.locale_code,
            "sample_terms": meta.common_land_terms[:5]
        })
    return res

@router.post("/detect")
def detect_language(req: DetectRequest) -> Dict[str, Any]:
    """Detects primary script, secondary scripts, and mixed-language ratios."""
    return LanguageDetectionService.detect_languages(req.text)

@router.post("/normalize")
def normalize_text(req: NormalizeRequest) -> Dict[str, Any]:
    """Normalizes Indic numerals, dates, and land units."""
    norm_num = TextNormalizationService.normalize_numerals(req.text)
    norm_area = TextNormalizationService.normalize_land_area(req.text)
    norm_date = TextNormalizationService.normalize_date(req.text)
    return {
        "original": req.text,
        "normalized_numerals": norm_num,
        "area_evaluation": norm_area,
        "date_evaluation": norm_date
    }

@router.get("/telemetry")
def get_language_telemetry() -> List[Dict[str, Any]]:
    """Returns model performance and verification telemetry by language."""
    return HumanVerificationService.get_language_telemetry_report()
