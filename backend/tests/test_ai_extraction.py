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
    assert ConfidenceService.get_tier(95.0) == "HIGH"
    assert ConfidenceService.get_tier(72.0) == "MEDIUM"
    assert ConfidenceService.get_tier(45.0) == "LOW"

def test_extraction_service_sync():
    res = ExtractionService.extract_fields_sync("Test deed raw text")
    assert res["average_confidence"] > 85.0
    assert "owner_name" in res["record_data"]
    assert res["confidence_evaluation"]["is_high_quality"] is True
