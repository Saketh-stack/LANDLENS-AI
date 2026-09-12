from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import  get_db
from backend.app.models import  CadastralRecord, LandRecord

router = APIRouter(prefix="/api/gis", tags=["GIS & Cadastral Mapping"])

@router.get("/parcels")
def get_cadastral_parcels(db: Session = Depends(get_db)):
    """
    Returns mock cadastral survey parcels with GeoJSON geometry and verification status
    """
    cadastral_list = db.query(CadastralRecord).all()
    features = []

    for c in cadastral_list:
        linked_record = db.query(LandRecord).filter(LandRecord.survey_number == c.survey_number).first()
        
        status = linked_record.status if linked_record else "UNCLAIMED"
        owner = linked_record.owner_name if linked_record else "Government / Forest / Unclaimed"
        classification = linked_record.land_classification if linked_record else "Revenue Land"
        
        # Center coordinate calculation for marker pin
        coords = c.coordinates_geojson.get("coordinates", [[]])[0]
        center_lat = sum(p[1] for p in coords) / len(coords) if coords else 23.2599
        center_lng = sum(p[0] for p in coords) / len(coords) if coords else 77.4126

        features.append({
            "type": "Feature",
            "properties": {
                "id": c.id,
                "survey_number": c.survey_number,
                "village": c.village,
                "district": c.district,
                "cadastral_area": c.cadastral_area,
                "survey_year": c.survey_year,
                "owner_name": owner,
                "land_classification": classification,
                "status": status,
                "center": [center_lat, center_lng],
                "verified": status in ["APPROVED", "PUBLISHED"]
            },
            "geometry": c.coordinates_geojson
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
