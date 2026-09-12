from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import  get_db
from backend.app.models import  LandRecord, Registration, CadastralRecord
from backend.app.services.mock_dept import MockRegistrationDepartmentService

router = APIRouter(prefix="/api/demo", tags=["Judge Demo Presets"])

@router.get("/scenarios")
def get_demo_scenarios():
    return [
        {
            "id": "scenario_1",
            "title": "Scenario 1: Successful Registration",
            "badge": "Happy Path",
            "description": "Standard registration arrives via mock API, OCR passes >90% confidence, business rules pass, officer verifies and publishes in 2-3 day window."
        },
        {
            "id": "scenario_2",
            "title": "Scenario 2: Low OCR Confidence",
            "badge": "Quality Alert",
            "description": "Scanned handwritten register triggers <80% confidence alert on Land Area & Survey number, forcing manual officer intervention."
        },
        {
            "id": "scenario_3",
            "title": "Scenario 3: Duplicate Survey Number",
            "badge": "Collision Warning",
            "description": "Deed attempts to register survey '101/2B' which already belongs to active landowner Suresh Patel. System blocks and flags duplicate."
        },
        {
            "id": "scenario_4",
            "title": "Scenario 4: Owner Mismatch",
            "badge": "Integrity Check",
            "description": "Extracted current landowner conflicts with historical ownership genealogy in the Land Registry."
        },
        {
            "id": "scenario_5",
            "title": "Scenario 5: Area Mismatch",
            "badge": "Cadastral Delta",
            "description": "Extracted sale deed specifies 2.45 Acres, but Cadastral Survey baseline is 2.40 Acres. System calculates 0.05 Acre delta."
        },
        {
            "id": "scenario_6",
            "title": "Scenario 6: Historical Document Digitization",
            "badge": "Multi-Step Pipeline",
            "description": "Upload scanned archival PDF/JPG with 8-stage visual stepper (Upload -> OCR -> NLP -> Validation -> Approval)."
        },
        {
            "id": "scenario_7",
            "title": "Scenario 7: AI Learning from Officer Correction",
            "badge": "Self-Improving AI",
            "description": "Officer corrects area from 2.45 to 2.40 Acres. System logs correction to AI feedback loop, boosting model accuracy."
        }
    ]

@router.post("/trigger/{scenario_id}")
def trigger_demo_scenario(scenario_id: str, db: Session = Depends(get_db)):
    if scenario_id == "scenario_1":
        reg = MockRegistrationDepartmentService.simulate_incoming_registration(db)
        return {"scenario": scenario_id, "message": "Triggered Successful Registration", "registration_id": reg.id}
    elif scenario_id == "scenario_2":
        reg = MockRegistrationDepartmentService.simulate_incoming_registration(db, scenario="low_confidence")
        return {"scenario": scenario_id, "message": "Triggered Low OCR Confidence Scenario", "registration_id": reg.id}
    elif scenario_id == "scenario_3":
        reg = MockRegistrationDepartmentService.simulate_incoming_registration(db, scenario="duplicate_survey")
        return {"scenario": scenario_id, "message": "Triggered Duplicate Survey Number Scenario", "registration_id": reg.id}
    elif scenario_id == "scenario_5":
        reg = MockRegistrationDepartmentService.simulate_incoming_registration(db, scenario="area_mismatch")
        return {"scenario": scenario_id, "message": "Triggered Cadastral Area Mismatch Scenario", "registration_id": reg.id}
    else:
        reg = MockRegistrationDepartmentService.simulate_incoming_registration(db)
        return {"scenario": scenario_id, "message": f"Demo scenario {scenario_id} initiated", "registration_id": reg.id}
