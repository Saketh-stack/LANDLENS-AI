import requests

def test_api():
    print("Testing backend logic directly...")
    from backend.app.database import SessionLocal
    from backend.app.models import LandRecord, CadastralRecord
    from backend.app.services.validation_engine import ValidationEngineService
    from backend.app.services.ai_extractor import AIExtractorService
    from backend.app.services.mock_dept import MockRegistrationDepartmentService

    db = SessionLocal()
    try:
        records = db.query(LandRecord).filter(LandRecord.is_public == True).all()
        print(f"Public approved records available: {len(records)}")
        assert len(records) >= 5, "Should have at least 5 public records"

        # Test AI Extraction
        ai_res = AIExtractorService.extract_structured_record("Sample deed text")
        print(f"AI Extraction average confidence: {ai_res['average_confidence']}%")
        assert "owner_name" in ai_res["record_data"], "Should extract owner_name"

        # Test Validation Engine Area Mismatch against Cadastral DB
        mismatch_data = {
            "owner_name": "Ravi Kumar",
            "survey_number": "123/4A",
            "village": "Rampur Kalan",
            "district": "Bhopal",
            "land_area": 2.45, # Cadastral is 2.40
            "registration_number": "REG-TEST-99",
            "registration_date": "01-09-2026"
        }
        val_res = ValidationEngineService.validate_record(mismatch_data, db)
        print(f"Validation Engine checked rules. Warnings: {val_res['has_warnings']}, Errors: {val_res['has_errors']}")
        # Ensure rule 7 caught the cadastral delta
        rule_7 = next((r for r in val_res["results"] if r["rule_id"] == "RULE-07"), None)
        assert rule_7 and rule_7["status"] == "WARNING", "Cadastral area delta should trigger warning"
        print("RULE-07 (Cadastral Cross-Check) passed assertion!")

        # Test Mock Registration Department Generation
        reg = MockRegistrationDepartmentService.simulate_incoming_registration(db)
        print(f"Simulated registration created: {reg.registration_number}, target date: {reg.expected_public_date}")
        assert reg.id is not None
        print("ALL BACKEND LOGIC VERIFICATION CHECKS PASSED!")
    finally:
        db.close()

if __name__ == "__main__":
    test_api()
