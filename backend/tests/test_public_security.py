import uuid
import pytest
from backend.app.core.database import SessionLocal
from backend.app.models.land_record import LandRecord
from backend.app.services.land_record_service import LandRecordService

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_public_records_returns_only_published(db_session):
    unique_reg = f"REG-INTERNAL-{uuid.uuid4().hex[:8].upper()}"
    unapproved = LandRecord(
        survey_number="999/INTERNAL",
        khasra_number="KHA-9999",
        khata_number="KH-9999",
        owner_name="Confidential Internal Owner",
        village="Test Village",
        tehsil="Test Tehsil",
        district="Test District",
        land_area=5.0,
        registration_number=unique_reg,
        registration_date="01-01-2026",
        status="OFFICER_REVIEW",
        is_public=False,
        publication_status="PENDING"
    )
    db_session.add(unapproved)
    db_session.commit()

    try:
        # Query public records
        public_records = LandRecordService.get_public_records(db=db_session)
        public_reg_nos = [r.registration_number for r in public_records]

        # Verify unapproved record is strictly absent
        assert unique_reg not in public_reg_nos
        for rec in public_records:
            assert rec.is_public is True
            assert rec.status in ["APPROVED", "PUBLISHED"]
    finally:
        db_session.delete(unapproved)
        db_session.commit()
