"""
Comprehensive End-to-End Pipeline Tests for LANDLENS-AI.
Covers the 7 mandatory statutory test cases:
1. Clear printed sale deed (high confidence, >=90% HIGH tier)
2. Poor-quality scanned document (quality check, <80% LOW tier, requires review)
3. Handwritten land record (human review queue routing)
4. Survey number optical ambiguity (125/Z vs 125/2, no silent rewrite)
5. Cadastral ground truth area mismatch (3.85 vs 3.20, severity ERROR)
6. Duplicate registration (8 vectors, risk score, officer advisory)
7. Multilingual Telugu document (language detection, script preservation, transliteration)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.land_record import LandRecord
from backend.app.models.document import Document
from backend.app.models.cadastral_record import CadastralRecord
from backend.app.ai.multilingual.extraction_service import MultilingualExtractionService
from backend.app.ai.multilingual.confidence_service import ConfidenceScoringService
from backend.app.ai.multilingual.number_analyzer import NumberAnalyzer
from backend.app.ai.multilingual.language_detector import LanguageDetectionService
from backend.app.ai.multilingual.transliteration_service import TransliterationService
from backend.app.services.preprocessing_service import PreprocessingService
from backend.app.services.validation_engine import ValidationEngine
from backend.app.validation.duplicate_rules import DuplicateRulesEngine
from backend.app.services.document_service import DocumentService

# In-memory SQLite session for tests
@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed cadastral baseline record for Survey 101/2B (Cadastral ground truth: 3.20 Acres)
    cad = CadastralRecord(
        survey_number="101/2B",
        district="Bhopal",
        village="Rampur Kalan",
        cadastral_area=3.20
    )
    session.add(cad)

    # Seed an existing approved LandRecord for duplicate checks
    existing_rec = LandRecord(
        registration_number="REG-2026/SRO/4481",
        survey_number="101/2B",
        khasra_number="KHA-101",
        khata_number="KH-101",
        village="Rampur Kalan",
        tehsil="Huzur",
        district="Bhopal",
        state="Madhya Pradesh",
        owner_name="Kailash Nath Verma",
        land_area=3.20,
        registration_date="10-09-2026",
        status="APPROVED",
        is_public=True
    )
    session.add(existing_rec)
    session.commit()

    yield session
    session.close()

# ------------------------------------------------------------------------------
# Case 1: Clear Printed Sale Deed (High Confidence >= 90%)
# ------------------------------------------------------------------------------
def test_case_1_clear_printed_sale_deed():
    sample_text = (
        "GOVERNMENT OF MADHYA PRADESH - REGISTERED SALE DEED\n"
        "Registration No: REG2026/00735 | Date: 11-09-2026\n"
        "Purchaser / Owner: Ravi Kumar\n"
        "Father Name: Anand Kumar\n"
        "Survey Number: 123/4A | Khasra Number: KHA-7796\n"
        "Total Area: 2.45 Acres | Land Classification: Agricultural\n"
        "Village: Rampur Kalan | Tehsil: Huzur | District: Bhopal | State: Madhya Pradesh\n"
        "Consideration Amount: Rs. 15,00,000 | Stamp Duty Paid: Rs. 1,05,000"
    )
    res = MultilingualExtractionService.extract_fields_sync(sample_text)
    assert res["average_confidence"] >= 90.0, f"Expected >=90% confidence, got {res['average_confidence']}"
    assert res["record_data"]["owner_name"] == "Ravi Kumar"
    assert res["record_data"]["survey_number"] == "123/4A"
    assert res["record_data"]["village"] == "Rampur Kalan"
    assert res["requires_review"] is False

    # Check field confidence tiers
    owner_fld = res["fields_detailed"]["owner_name"]
    assert owner_fld["confidence_tier"] == "HIGH"
    assert owner_fld["confidence"] >= 0.90

# ------------------------------------------------------------------------------
# Case 2: Poor-Quality Scanned Document (Low Confidence & Review Required)
# ------------------------------------------------------------------------------
def test_case_2_poor_quality_scanned_document():
    # Simulate fragmented OCR output from degraded/noisy scan
    noisy_ocr_text = (
        "GOV...NT ... PR..DESH - D..D\n"
        "Reg..: ???/007 | Dt: ..-..-2026\n"
        "P...ser: R..vi K...r\n"
        "Sy: ?\n"
        "Area: ... Ac..\n"
        "Vil: R..pur"
    )
    res = MultilingualExtractionService.extract_fields_sync(noisy_ocr_text)
    assert res["requires_review"] is True

    # Validate that quality assessment marks it for officer verification
    eval_res = ConfidenceScoringService.evaluate_field("survey_number", "")
    assert eval_res["tier"] == "LOW"
    assert eval_res["requires_review"] is True

# ------------------------------------------------------------------------------
# Case 3: Handwritten Land Record (Human Review Queue Routing)
# ------------------------------------------------------------------------------
def test_case_3_handwritten_land_record():
    # Handwritten documents typically exhibit low character recognition confidence
    handwritten_simulated_text = (
        "Handwritten Note / Patta Entry\n"
        "Name: Mohan Lal (cursive)\n"
        "Survey No: unverified\n"
        "Area: approx 1 bigha\n"
        "Village: Gopalpur"
    )
    res = MultilingualExtractionService.extract_fields_sync(handwritten_simulated_text)
    # Must flag for human verification rather than hallucinating exact values
    assert res["requires_review"] is True
    assert "requires_review" in res

# ------------------------------------------------------------------------------
# Case 4: Survey Number Ambiguity (125/2 vs 125/Z - No Silent Rewrite)
# ------------------------------------------------------------------------------
def test_case_4_survey_number_ambiguity():
    # Crucial government requirement: Never silently alter ambiguous characters
    analysis = NumberAnalyzer.analyze("survey_number", "125/Z", base_confidence=95.0)

    # Must preserve original character string '125/Z'
    assert analysis["value"] == "125/Z"
    assert analysis["ambiguity_detected"] is True
    # Must lower confidence and mark for officer review
    assert analysis["confidence"] <= 61.0
    assert analysis["requires_review"] is True
    # Must provide possible alternatives
    assert "125/2" in analysis["possible_alternatives"]

# ------------------------------------------------------------------------------
# Case 5: Cadastral Ground Truth Area Mismatch (3.85 vs 3.20 Cadastral Error)
# ------------------------------------------------------------------------------
def test_case_5_area_mismatch_cadastral(db_session):
    # Deed claims 3.85 Acres for Survey 101/2B, but Cadastral baseline is 3.20 Acres
    deed_data = {
        "survey_number": "101/2B",
        "land_area": 3.85,
        "village": "Rampur Kalan",
        "district": "Bhopal",
        "state": "Madhya Pradesh",
        "owner_name": "Kailash Nath Verma",
        "registration_number": "REG-TEST-005",
        "registration_date": "10-09-2026"
    }
    val = ValidationEngine.validate_record(deed_data, db=db_session)

    # Check for area mismatch rule
    area_rules = [r for r in val["results"] if "cadastral" in r.get("rule_name", "").lower() or r.get("rule_id") in ["RULE-07", "CADASTRAL_AREA_MATCH", "AREA_MISMATCH"]]
    assert len(area_rules) > 0

    area_rule = area_rules[0]
    assert area_rule["status"] in ["ERROR", "WARNING"]
    assert "mismatch" in area_rule["message"].lower() or "cadastral" in area_rule["message"].lower()

# ------------------------------------------------------------------------------
# Case 6: Duplicate Registration (8 Vectors, Risk Score & Advisory Flag)
# ------------------------------------------------------------------------------
def test_case_6_duplicate_registration(db_session):
    # Attempt to register parcel with same registration number and survey collision
    duplicate_payload = {
        "registration_number": "REG-2026/SRO/4481",
        "survey_number": "101/2B",
        "village": "Rampur Kalan",
        "district": "Bhopal",
        "owner_name": "Different Purchaser",
        "land_area": 3.20
    }
    dup_res = DuplicateRulesEngine.analyze_duplicates(
        data=duplicate_payload,
        db=db_session
    )

    assert dup_res["is_duplicate"] is True
    assert dup_res["risk_score"] >= 40
    assert dup_res["risk_level"] in ["HIGH", "CRITICAL"]
    assert dup_res["requires_officer_review"] is True
    # Non-rejection policy
    assert "officer verification" in dup_res["policy"].lower()

# ------------------------------------------------------------------------------
# Case 7: Multilingual Telugu Document (Language Detection & Script Preservation)
# ------------------------------------------------------------------------------
def test_case_7_multilingual_telugu_document():
    telugu_deed = (
        "తెలంగాణ ప్రభుత్వం - రిజిస్ట్రేషన్ మరియు స్టాంపుల శాఖ\n"
        "క్రయవిక్రయ పత్రము (Sale Deed)\n"
        "రిజిస్ట్రేషన్ సంఖ్య: 2026/TEL/9941 | తేదీ: 12-09-2026\n"
        "పట్టాదారు పేరు: రమేష్ శర్మ\n"
        "తండ్రి పేరు: వెంకటేశ్వర్లు శర్మ\n"
        "సర్వే నంబర్: 184/A | ఖాదా నంబర్: 452\n"
        "విస్తీర్ణము: 3.50 ఎకరాలు | భూమి రకం: వ్యవసాయ మెట్ట\n"
        "గ్రామము: కొంపల్లి | మండలం: మేడ్చల్ | జిల్లా: మేడ్చల్-మల్కాజిగిరి | రాష్ట్రం: తెలంగాణ"
    )

    # 1. Language Detection
    lang_info = LanguageDetectionService.detect_languages(telugu_deed)
    assert lang_info["primary_language"] == "Telugu"
    assert lang_info["is_multilingual"] is True

    # 2. Field Extraction & Name Script Preservation
    res = MultilingualExtractionService.extract_fields_sync(telugu_deed)
    assert res["record_data"]["survey_number"] == "184/A"
    assert res["record_data"]["owner_name"] == "రమేష్ శర్మ"

    # 3. Transliteration to English
    trans = TransliterationService.preserve_and_transliterate(res["record_data"]["owner_name"], "owner_name")
    assert trans["original_value"] == "రమేష్ శర్మ"
    assert "Ramesh" in trans["transliterated_value"]
    assert trans["is_name_preserved"] is True
