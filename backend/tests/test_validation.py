import pytest
from backend.app.core.database import SessionLocal
from backend.app.validation.rules import BusinessRulesEngine
from backend.app.validation.cross_database_rules import CrossDatabaseRulesEngine

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_rule_01_mandatory_fields():
    # Incomplete record
    incomplete = {"owner_name": "Ravi Kumar"}
    res = BusinessRulesEngine.validate_all(incomplete)
    rule_1 = next(r for r in res["results"] if r["rule_id"] == "RULE-01")
    assert rule_1["status"] == "ERROR"
    assert res["has_errors"] is True

def test_rule_03_land_area_sanity():
    # Negative area
    invalid_area = {
        "owner_name": "Ravi Kumar",
        "survey_number": "123/4A",
        "village": "Rampur Kalan",
        "district": "Bhopal",
        "land_area": -5.0,
        "registration_number": "REG-TEST-01"
    }
    res = BusinessRulesEngine.validate_all(invalid_area)
    rule_3 = next(r for r in res["results"] if r["rule_id"] == "RULE-03")
    assert rule_3["status"] == "ERROR"

def test_rule_07_cadastral_cross_check_warning(db_session):
    # Survey 123/4A in cadastral DB has area 2.40 Ac. Deed has 2.45 Ac.
    mismatch = {
        "owner_name": "Ravi Kumar",
        "survey_number": "123/4A",
        "village": "Rampur Kalan",
        "district": "Bhopal",
        "land_area": 2.45,
        "registration_number": "REG-TEST-02",
        "registration_date": "01-09-2026"
    }
    res = BusinessRulesEngine.validate_all(mismatch, db=db_session)
    rule_7 = next(r for r in res["results"] if r["rule_id"] == "RULE-07")
    assert rule_7["status"] == "WARNING"
    assert "Area mismatch detected" in rule_7["message"]
    assert res["has_warnings"] is True

def test_cross_database_engine(db_session):
    reconcile_res = CrossDatabaseRulesEngine.reconcile_cadastral_ground_truth(
        survey_number="123/4A",
        deed_area=2.45,
        village="Rampur Kalan",
        district="Bhopal",
        db=db_session
    )
    assert reconcile_res["matched"] is True
    assert reconcile_res["has_discrepancy"] is True
    assert reconcile_res["recommended_action"] == "SYNC_TO_CADASTRAL"
