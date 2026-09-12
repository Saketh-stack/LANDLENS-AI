from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_roles
from backend.app.models.state import State
from backend.app.models.state_configuration import StateConfiguration
from backend.app.models.district import District
from backend.app.integrations.government_adapter import GovernmentStateAdapter

router = APIRouter(prefix="/api/admin", tags=["Administration & Pan-India Setup"])

@router.get("/states")
def get_pan_india_states(db: Session = Depends(get_db)):
    states = db.query(State).all()
    results = []
    for s in states:
        prof = GovernmentStateAdapter.get_state_profile(s.name)
        results.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "capital": s.capital,
            "region": s.region,
            "survey_label": prof["survey_label"],
            "admin_unit_label": prof["admin_unit"],
            "area_unit": prof["area_unit"],
            "ror_label": prof["ror_label"]
        })
    return results

@router.get("/district-progress")
def get_district_progress():
    return [
        {"district": "Bhopal", "total": 4200, "digitized": 3950, "accuracy": 95.1},
        {"district": "Indore", "total": 3800, "digitized": 3420, "accuracy": 94.8},
        {"district": "Jabalpur", "total": 2900, "digitized": 2600, "accuracy": 93.6},
        {"district": "Gwalior", "total": 2400, "digitized": 2100, "accuracy": 92.9},
        {"district": "Ujjain", "total": 1950, "digitized": 1720, "accuracy": 94.2}
    ]
