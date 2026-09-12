"""
Multilingual Recognition & Processing Package for Indian Land Records.
Exporting all core services.
"""
from backend.app.ai.multilingual.languages import LanguageConfiguration, LanguageMeta
from backend.app.ai.multilingual.language_detector import LanguageDetectionService
from backend.app.ai.multilingual.normalizer import TextNormalizationService
from backend.app.ai.multilingual.field_dictionary import MultilingualFieldDictionary
from backend.app.ai.multilingual.transliteration_service import TransliterationService
from backend.app.ai.multilingual.translation_service import TranslationService
from backend.app.ai.multilingual.ocr_service import MultilingualOCRService
from backend.app.ai.multilingual.extraction_service import LandFieldExtractionService
from backend.app.ai.multilingual.confidence_service import ConfidenceScoringService
from backend.app.ai.multilingual.verification_service import HumanVerificationService

__all__ = [
    "LanguageConfiguration",
    "LanguageMeta",
    "LanguageDetectionService",
    "TextNormalizationService",
    "MultilingualFieldDictionary",
    "TransliterationService",
    "TranslationService",
    "MultilingualOCRService",
    "LandFieldExtractionService",
    "ConfidenceScoringService",
    "HumanVerificationService"
]
