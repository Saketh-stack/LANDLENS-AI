from typing import Dict, Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.validation import ValidationSummaryOut
from backend.app.services.validation_service import ValidationService

router = APIRouter(prefix="/api/validation", tags=["Validation Engine"])

@router.post("/validate-record", response_model=ValidationSummaryOut)
def validate_record(record_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    return ValidationService.validate_record_data(record_data, db=db)

@router.get("/rules")
def get_validation_rules_catalog():
    return {
        "total_rules": 14,
        "rules": [
            {"id": "RULE-01", "name": "Mandatory Fields Check", "severity": "ERROR"},
            {"id": "RULE-02", "name": "Survey Number Syntax Validation", "severity": "WARNING"},
            {"id": "RULE-03", "name": "Land Area Positive & Boundary Sanity", "severity": "ERROR"},
            {"id": "RULE-04", "name": "Owner Identity & Lineage Integrity", "severity": "WARNING"},
            {"id": "RULE-05", "name": "Registration Date Chronology", "severity": "ERROR"},
            {"id": "RULE-06", "name": "Administrative Hierarchy Consistency", "severity": "WARNING"},
            {"id": "RULE-07", "name": "Cadastral Ground Truth Area Cross-Check", "severity": "WARNING"},
            {"id": "RULE-08", "name": "Land Classification Legitimacy", "severity": "WARNING"},
            {"id": "RULE-09", "name": "Deed Type Recognition", "severity": "WARNING"},
            {"id": "RULE-10", "name": "Sub-Registrar Office Seal Verification", "severity": "PASS"},
            {"id": "RULE-11", "name": "Mutation & Prior Encumbrance Check", "severity": "PASS"},
            {"id": "RULE-12", "name": "Duplicate Registration Number Check", "severity": "ERROR"},
            {"id": "RULE-13", "name": "Spatial Boundary & Polygon Sanity", "severity": "PASS"},
            {"id": "RULE-14", "name": "AI OCR Extraction Confidence Gate", "severity": "WARNING"}
        ]
    }
