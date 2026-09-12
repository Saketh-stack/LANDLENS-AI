import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.registration import Registration
from backend.app.models.cadastral_record import CadastralRecord
from backend.app.models.audit_log import AuditLog

class RegistrationDepartmentAdapter:
    """
    Sub-Registrar Office (SRO) Integration Simulator.
    Simulates newly registered sale deeds ingested from state registration portals (e.g. CCLA/IGRS/Kaveri/Bhoomi/e-PMAY).
    """
    MOCK_TEMPLATES = [
        {
            "owner_name": "Ravi Kumar",
            "father_husband_name": "Anand Kumar",
            "survey_number": "123/4A",
            "khasra_number": "KHA-7796",
            "khata_number": "KH-27159",
            "village": "Rampur Kalan",
            "tehsil": "Huzur",
            "district": "Bhopal",
            "state": "Madhya Pradesh",
            "land_area": 2.45,  # Deliberate 0.05 Ac delta against Cadastral 2.40 for Judge demo
            "land_classification": "Agricultural"
        },
        {
            "owner_name": "K. Chandra Shekhar",
            "father_husband_name": "K. Rama Rao",
            "survey_number": "78/A",
            "khasra_number": "KHA-9014",
            "khata_number": "KH-2231",
            "village": "Shamshabad Rural",
            "tehsil": "Shamshabad",
            "district": "Ranga Reddy",
            "state": "Telangana",
            "land_area": 0.95,
            "land_classification": "Agricultural"
        },
        {
            "owner_name": "Suresh Kumar Patel",
            "father_husband_name": "Dinesh Patel",
            "survey_number": "101/2B",
            "khasra_number": "KHA-1092",
            "khata_number": "KH-5541",
            "village": "Rampur Kalan",
            "tehsil": "Huzur",
            "district": "Bhopal",
            "state": "Madhya Pradesh",
            "land_area": 1.80,
            "land_classification": "Agricultural"
        }
    ]

    @classmethod
    def simulate_incoming_registration(cls, db: Session, scenario_override: Optional[Dict[str, Any]] = None) -> Registration:
        now = datetime.now()
        target_date = now + timedelta(days=random.choice([2, 3]))

        template = scenario_override if scenario_override else random.choice(cls.MOCK_TEMPLATES).copy()
        seq = random.randint(100, 999)
        reg_no = f"REG{now.year}/{seq:05d}"

        # Check for cadastral area discrepancy
        cad = db.query(CadastralRecord).filter(CadastralRecord.survey_number == template["survey_number"]).first()
        has_mismatch = False
        mismatch_details = None
        if cad and abs(cad.cadastral_area - template["land_area"]) > 0.01:
            has_mismatch = True
            mismatch_details = (
                f"Area mismatch detected: Incoming Registered Deed specifies {template['land_area']} Acres, "
                f"while official Cadastral Ground Truth records {cad.cadastral_area} Acres."
            )

        reg = Registration(
            registration_number=reg_no,
            source="Sub-Registrar Office (State IGRS Mock API)",
            owner_name=template["owner_name"],
            father_husband_name=template.get("father_husband_name", ""),
            survey_number=template["survey_number"],
            khasra_number=template.get("khasra_number", f"KHA-{random.randint(1000, 9999)}"),
            khata_number=template.get("khata_number", f"KH-{random.randint(10000, 99999)}"),
            village=template["village"],
            tehsil=template["tehsil"],
            district=template["district"],
            state=template.get("state", "Madhya Pradesh"),
            land_area=template["land_area"],
            land_classification=template.get("land_classification", "Agricultural"),
            registration_date=now.strftime("%d-%m-%Y"),
            expected_public_date=target_date.strftime("%d-%m-%Y (Within 2-3 days SLA)"),
            document_name=f"Deed_{reg_no.replace('/', '_')}.pdf",
            status="RECEIVED",
            confidence_score=92.5,
            has_mismatch=has_mismatch,
            mismatch_details=mismatch_details
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        # Audit trail
        audit = AuditLog(
            actor="SRO Integration Gateway",
            actor_role="SYSTEM",
            action="REGISTRATION_INGESTED",
            entity_type="REGISTRATION",
            entity_id=str(reg.id),
            details=f"New deed received: {reg.registration_number} for owner {reg.owner_name} ({reg.land_area} Ac)"
        )
        db.add(audit)
        db.commit()

        return reg
