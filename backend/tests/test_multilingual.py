"""
Unit and Integration Tests for Multilingual Indian Land Records Recognition Pipeline.
Tests 13 Indian languages, script detection, Indic numeral & unit normalization,
personal name preservation, and confidence scoring.
"""
import pytest
from backend.app.ai.multilingual.languages import LanguageConfiguration
from backend.app.ai.multilingual.language_detector import LanguageDetectionService
from backend.app.ai.multilingual.normalizer import TextNormalizationService
from backend.app.ai.multilingual.field_dictionary import MultilingualFieldDictionary
from backend.app.ai.multilingual.transliteration_service import TransliterationService
from backend.app.ai.multilingual.translation_service import TranslationService
from backend.app.ai.multilingual.confidence_service import ConfidenceScoringService

class TestLanguageConfiguration:
    def test_thirteen_languages_registered(self):
        langs = LanguageConfiguration.get_supported_codes()
        assert len(langs) >= 13
        expected = ["en", "hi", "te", "ta", "kn", "ml", "mr", "gu", "bn", "pa", "or", "as", "ur"]
        for code in expected:
            assert code in langs
            meta = LanguageConfiguration.get_language(code)
            assert meta is not None
            assert len(meta.native_name) > 0
            assert len(meta.script) > 0

class TestLanguageDetectionService:
    def test_english_detection(self):
        text = "Government of Telangana Registration Department Sale Deed"
        res = LanguageDetectionService.detect_languages(text)
        assert res["primary_code"] == "en"
        assert not res["is_mixed"]

    def test_telugu_detection(self):
        text = "తెలంగాణ ప్రభుత్వం రిజిస్ట్రేషన్ మరియు స్టాంపుల శాఖ క్రయవిక్రయ పత్రము"
        res = LanguageDetectionService.detect_languages(text)
        assert res["primary_code"] == "te"
        assert res["primary_name"] == "Telugu"

    def test_hindi_detection(self):
        text = "उत्तर प्रदेश शासन निबंधन विभाग बैनामा विक्रय पत्र भू-स्वामी"
        res = LanguageDetectionService.detect_languages(text)
        assert res["primary_code"] == "hi"
        assert res["primary_name"] == "Hindi"

    def test_tamil_detection(self):
        text = "தமிழ்நாடு அரசு பதிவுத்துறை கிரய பத்திரம் நில உரிமையாளர்"
        res = LanguageDetectionService.detect_languages(text)
        assert res["primary_code"] == "ta"
        assert res["primary_name"] == "Tamil"

    def test_mixed_language_detection(self):
        # Telugu + English document text
        text = "తెలంగాణ ప్రభుత్వం Sale Deed No 4521/2023 సర్వే నంబరు 184/A Shamshabad village"
        res = LanguageDetectionService.detect_languages(text)
        assert res["is_mixed"] is True
        codes = [d["code"] for d in res["distributions"]]
        assert "te" in codes
        assert "en" in codes

class TestTextNormalizationService:
    def test_indic_numeral_conversion(self):
        # Devanagari numerals
        assert TextNormalizationService.normalize_numerals("सर्वे १२३/४") == "सर्वे 123/4"
        # Telugu numerals
        assert TextNormalizationService.normalize_numerals("సర్వే ౧౮౪/ఎ") == "సర్వే 184/ఎ"
        # Tamil numerals
        assert TextNormalizationService.normalize_numerals("சர்வே ௧௨௩") == "சர்வே 123"
        # Bengali numerals
        assert TextNormalizationService.normalize_numerals("দাগ ১২৩") == "দাগ 123"

    def test_land_area_normalization(self):
        # Guntas conversion (40 Guntas = 1 Acre)
        norm_gun = TextNormalizationService.normalize_land_area("20 Guntas")
        assert norm_gun["normalized_acres"] == 0.5
        assert norm_gun["unit"] == "Guntas"

        # Cents conversion (100 Cents = 1 Acre)
        norm_cent = TextNormalizationService.normalize_land_area("50 Cents")
        assert norm_cent["normalized_acres"] == 0.5

        # Pure acres
        norm_acre = TextNormalizationService.normalize_land_area("2.45 Acres")
        assert norm_acre["normalized_acres"] == 2.45

        # Indic numerals inside area
        norm_indic = TextNormalizationService.normalize_land_area("२.५ एकड़")
        assert norm_indic["normalized_acres"] == 2.5

    def test_date_normalization(self):
        # DD/MM/YYYY
        dt1 = TextNormalizationService.normalize_date("14/08/2023")
        assert dt1["normalized_iso"] == "2023-08-14"

        # Indic digits date
        dt2 = TextNormalizationService.normalize_date("१४/०८/२०२३")
        assert dt2["normalized_iso"] == "2023-08-14"

    def test_survey_number_normalization(self):
        sy = TextNormalizationService.normalize_survey_number("184 / a")
        assert sy["normalized"] == "184/A"
        sy_indic = TextNormalizationService.normalize_survey_number("१८४/क")
        assert "184" in sy_indic["normalized"]

class TestFieldDictionaryAndTransliteration:
    def test_field_dictionary_synonyms(self):
        assert MultilingualFieldDictionary.find_canonical_field("భూయజమాని") == "owner_name"
        assert MultilingualFieldDictionary.find_canonical_field("खातेदार") == "owner_name"
        assert MultilingualFieldDictionary.find_canonical_field("సర్వే నంబరు") == "survey_number"
        assert MultilingualFieldDictionary.find_canonical_field("खसरा") == "survey_number"
        assert MultilingualFieldDictionary.find_canonical_field("பரப்பளவு") == "land_area"

    def test_name_preservation(self):
        # Ensure name is not translated to English vocabulary
        trans = TransliterationService.preserve_and_transliterate("రమేష్ శర్మ", "owner_name")
        assert trans["original_value"] == "రమేష్ శర్మ"
        assert "Ramesh" in trans["transliterated_value"]
        assert "Sharma" in trans["transliterated_value"]
        assert trans["is_name_preserved"] is True

    def test_translation_with_legal_disclaimer(self):
        trans = TranslationService.translate_legal_term("క్రయవిక్రయ పత్రము")
        assert "Sale Deed" in trans["translated"]
        assert "LEGAL FACTUALITY NOTICE" in trans["disclaimer"]

class TestConfidenceScoringService:
    def test_high_confidence(self):
        eval_res = ConfidenceScoringService.evaluate_field("survey_number", "184/A", base_confidence=92.0)
        assert eval_res["tier"] == "HIGH"
        assert not eval_res["needs_verification"]

    def test_low_confidence_needs_verification(self):
        eval_res = ConfidenceScoringService.evaluate_field("survey_number", "", base_confidence=30.0)
        assert eval_res["tier"] == "LOW"
        assert eval_res["needs_verification"] is True
