import random
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.models import  Registration, LandRecord, CadastralRecord, AuditLog

SAMPLE_OWNERS = [
    ("Ravi Kumar", "Anand Kumar", "Agricultural"),
    ("Suresh Patel", "Ishwarbhai Patel", "Agricultural"),
    ("Lakshmi Devi", "K. Venkatesh", "Residential"),
    ("Priya Sharma", "Rajesh Sharma", "Commercial"),
    ("Mohanlal Verma", "Babulal Verma", "Agricultural"),
    ("Sunita Meena", "Devendra Meena", "Agricultural"),
    ("Vikram Singh", "Mahendra Singh", "Industrial"),
    ("Ananya Roy", "Subhash Roy", "Residential")
]

SAMPLE_VILLAGES = [
    ("Rampur Kalan", "Huzur", "Bhopal", "Madhya Pradesh"),
    ("Berasia Khurd", "Berasia", "Bhopal", "Madhya Pradesh"),
    ("Sanwer Dehat", "Sanwer", "Indore", "Madhya Pradesh"),
    ("Shamshabad Rural", "Shamshabad", "Ranga Reddy", "Telangana"),
    ("Mandideep Outskirts", "Goharganj", "Raisen", "Madhya Pradesh")
]

class MockRegistrationDepartmentService:
    """
    Simulates external Registration Department (Sub-Registrar Office) integrations.
    Generates realistic registered property deeds, emits webhook-like events to DoLR,
    and supports Fast Demo Mode for the proposed 2-3 day public viewing target.
    """

    @classmethod
    def simulate_incoming_registration(cls, db: Session, scenario: str = None) -> Registration:
        now = datetime.utcnow()
        reg_year = now.year
        seq_no = random.randint(100, 999)
        reg_number = f"REG{reg_year}/{seq_no:05d}"
        
        # Proposed prototype target: Public viewing available within 2-3 days
        target_availability = now + timedelta(days=2)

        if scenario == 'duplicate_survey':
            owner, father, classification = "Ramesh Gupta", "Kailash Gupta", "Agricultural"
            village, tehsil, district, state = "Rampur Kalan", "Huzur", "Bhopal", "Madhya Pradesh"
            survey_no = "101/2B" # Deliberately triggers duplicate survey warning
            area = 2.50
        elif scenario == 'area_mismatch':
            owner, father, classification = "Ravi Kumar", "Anand Kumar", "Agricultural"
            village, tehsil, district, state = "Rampur Kalan", "Huzur", "Bhopal", "Madhya Pradesh"
            survey_no = "123/4A"
            area = 2.45 # Mismatches cadastral database ground truth of 2.40 Acres
        elif scenario == 'low_confidence':
            owner, father, classification = "Bhanu Pratap", "Raghunath", "Agricultural"
            village, tehsil, district, state = "Berasia Khurd", "Berasia", "Bhopal", "Madhya Pradesh"
            survey_no = "142/9"
            area = 1.75
        else:
            owner_info = random.choice(SAMPLE_OWNERS)
            owner, father, classification = owner_info
            geo_info = random.choice(SAMPLE_VILLAGES)
            village, tehsil, district, state = geo_info
            sub_div = random.choice(['1A', '2B', '3C', '4', '1/2'])
            survey_no = f"{random.randint(110, 399)}/{sub_div}"
            area = round(random.uniform(0.75, 4.50), 2)

        reg = Registration(
            registration_number=reg_number,
            source="Registration Department (e-Registration SRO API Mock)",
            owner_name=owner,
            father_husband_name=father,
            survey_number=survey_no,
            khasra_number=f"KHA-{random.randint(2000, 9999)}",
            khata_number=f"KH-{random.randint(10000, 50000)}",
            village=village,
            tehsil=tehsil,
            district=district,
            state=state,
            land_area=area,
            land_classification=classification,
            registration_date=now.strftime("%d-%m-%Y"),
            expected_public_date=target_availability.strftime("%d-%m-%Y"),
            document_name=f"sale_deed_{reg_number.replace('/', '_')}.pdf",
            status="RECEIVED",
            confidence_score=92.5
        )

        db.add(reg)
        
        # Log system receipt in Audit trail
        audit = AuditLog(
            actor="Registration Dept Mock Gateway",
            actor_role="SYSTEM",
            action="NEW_REGISTRATION_RECEIVED",
            entity_type="REGISTRATION",
            entity_id=reg_number,
            details=f"Received registered sale deed for Owner: {owner}, Survey No: {survey_no}, Village: {village}"
        )
        db.add(audit)
        db.commit()
        db.refresh(reg)
        return reg
