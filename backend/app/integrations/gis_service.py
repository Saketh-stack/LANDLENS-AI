from typing import Dict, Any, List, Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger

class GISService:
    """
    GIS & Spatial Integration Service.
    Seamlessly integrates Google Maps Geocoding and Leaflet Cadastral boundaries,
    with graceful degradation when keys are absent.
    """
    @classmethod
    def get_gis_status(cls) -> Dict[str, Any]:
        if not settings.is_google_maps_enabled:
            return {
                "enabled": False,
                "message": "GIS integration is not configured. Using local cadastral coordinates.",
                "provider": "Local GeoJSON / Leaflet"
            }
        return {
            "enabled": True,
            "message": "Google Maps GIS Integration Active",
            "provider": "Google Maps Platform"
        }

    @classmethod
    async def geocode_address(cls, address: str) -> Dict[str, Any]:
        if not settings.is_google_maps_enabled:
            return {
                "enabled": False,
                "message": "GIS integration is not configured",
                "location": None
            }

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": settings.GOOGLE_GEOCODING_API_KEY or settings.GOOGLE_MAPS_API_KEY
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    loc = data["results"][0]["geometry"]["location"]
                    return {
                        "enabled": True,
                        "location": {"lat": loc["lat"], "lng": loc["lng"]},
                        "formatted_address": data["results"][0]["formatted_address"]
                    }
                return {
                    "enabled": True,
                    "message": f"Google Maps geocoding status: {data.get('status')}",
                    "location": None
                }
        except Exception as e:
            logger.error(f"Geocoding request failed: {e}")
            return {
                "enabled": False,
                "message": f"Geocoding service error: {str(e)}",
                "location": None
            }
