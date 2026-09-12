import asyncio
import pytest
from backend.app.integrations.gis_service import GISService

def test_gis_graceful_status_when_key_missing():
    status = GISService.get_gis_status()
    assert "enabled" in status
    assert "message" in status
    if not status["enabled"]:
        assert status["message"] == "GIS integration is not configured. Using local cadastral coordinates."

def test_geocoding_graceful_fallback():
    result = asyncio.run(GISService.geocode_address("Bhopal, Madhya Pradesh"))
    assert "enabled" in result
    assert "message" in result or "location" in result
    if not result["enabled"]:
        assert result["message"] == "GIS integration is not configured"
        assert result["location"] is None
