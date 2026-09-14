import pytest
from backend.app.ai.mock_ai_service import MockAIService
from backend.app.ai.confidence_service import ConfidenceService
from backend.app.ai.extraction_service import ExtractionService

def test_deterministic_ai_extraction():
    data = MockAIService.get_deterministic_extraction()
    assert "record_data" in data
    assert "owner_name" in data["record_data"]
    assert "survey_number" in data["record_data"]
    assert "bounding_boxes" in data
    assert data["average_confidence"] > 80.0

def test_confidence_tiers():
    # Enforce Section 8 standards: 90-100% HIGH, 80-89% MEDIUM, Below 80% LOW
    assert ConfidenceService.get_tier(95.0) == "HIGH"
    assert ConfidenceService.get_tier(84.0) == "MEDIUM"
    assert ConfidenceService.get_tier(72.0) == "LOW"
    assert ConfidenceService.get_tier(45.0) == "LOW"

def test_extraction_service_sync():
    sample_deed = (
        "GOVERNMENT OF MADHYA PRADESH - REGISTERED SALE DEED\n"
        "Registration No: REG2026/00735 | Date: 11-09-2026\n"
        "Purchaser / Owner: Ravi Kumar\n"
        "Father Name: Anand Kumar\n"
        "Survey Number: 123/4A | Khasra Number: KHA-7796\n"
        "Total Area: 2.45 Acres | Land Classification: Agricultural\n"
        "Village: Rampur Kalan | Tehsil: Huzur | District: Bhopal | State: Madhya Pradesh"
    )
    res = ExtractionService.extract_fields_sync(sample_deed)
    assert res["average_confidence"] >= 85.0
    assert res["record_data"]["owner_name"] == "Ravi Kumar"
    assert res["record_data"]["survey_number"] == "123/4A"
    assert res["record_data"]["land_area"] == 2.45
    assert "fields_detailed" in res
    assert res["fields_detailed"]["owner_name"]["confidence"] >= 0.90
