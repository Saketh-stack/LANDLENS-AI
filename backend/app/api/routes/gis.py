from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.integrations.gis_service import GISService
from backend.app.models.cadastral_record import CadastralRecord
from backend.app.models.land_record import LandRecord

router = APIRouter(prefix="/api/gis", tags=["GIS & Cadastral Mapping"])

@router.get("/config")
def get_gis_config():
    return GISService.get_gis_status()

@router.get("/geocode")
async def geocode_address(address: str = Query(..., min_length=2)):
    return await GISService.geocode_address(address)

@router.get("/parcels")
def get_cadastral_parcels(db: Session = Depends(get_db)):
    """
    Returns geo-referenced Cadastral survey parcel polygons for Leaflet GIS rendering.
    """
    cad_records = db.query(CadastralRecord).all()
    features = []

    for cad in cad_records:
        # Cross check corresponding land record status
        matched_rec = db.query(LandRecord).filter(LandRecord.survey_number == cad.survey_number).first()
        status = matched_rec.status if matched_rec else "UNVERIFIED"
        owner_name = matched_rec.owner_name if matched_rec else "Official Revenue Cadastre"

        features.append({
            "id": cad.id,
            "survey_number": cad.survey_number,
            "village": cad.village,
            "district": cad.district,
            "cadastral_area": cad.cadastral_area,
            "status": status,
            "owner_name": owner_name,
            "coordinates_geojson": cad.coordinates_geojson
        })

    return {
        "type": "FeatureCollection",
        "total_parcels": len(features),
        "parcels": features
    }
