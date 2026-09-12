import json
import os
from datetime import datetime
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models import (
    State,
    District,
    AdministrativeUnit,
    Village,
    StateConfiguration,
    User,
    LandRecord,
    CadastralRecord,
    Registration,
    AuditLog
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sample_data"))

        # 1. Seed Pan-India States & State Configurations
        states_path = os.path.join(sample_dir, "states_seed.json")
        if os.path.exists(states_path) and db.query(State).count() == 0:
            with open(states_path, "r", encoding="utf-8") as f:
                states_data = json.load(f)
            for s in states_data:
                state_obj = State(
                    name=s["name"],
                    code=s["code"],
                    capital=s.get("capital"),
                    region=s.get("region")
                )
                db.add(state_obj)
                db.flush()

                cfg = StateConfiguration(
                    state_id=state_obj.id,
                    survey_number_label=s.get("survey_label", "Survey Number"),
                    admin_unit_label=s.get("admin_unit_label", "Tehsil"),
                    default_area_unit=s.get("default_area_unit", "Acres"),
                    language_code=s.get("language_code", "en")
                )
                db.add(cfg)
            db.commit()
            print(f"Seeded {len(states_data)} Pan-India States and configurations.")

        # 2. Seed Districts and Administrative Units
        dist_path = os.path.join(sample_dir, "districts_seed.json")
        if os.path.exists(dist_path) and db.query(District).count() == 0:
            with open(dist_path, "r", encoding="utf-8") as f:
                dist_data = json.load(f)
            for d in dist_data:
                st = db.query(State).filter(State.code == d["state_code"]).first()
                if st:
                    dist_obj = District(state_id=st.id, name=d["district_name"])
                    db.add(dist_obj)
                    db.flush()
                    for au in d.get("admin_units", []):
                        db.add(AdministrativeUnit(district_id=dist_obj.id, name=au, unit_type=st.configurations.admin_unit_label if st.configurations else "Tehsil"))
            db.commit()
            print("Seeded districts and administrative units.")

        # 3. Seed Users
        if db.query(User).count() == 0:
            users = [
                User(
                    username="officer",
                    email="officer@dolr.gov.in",
                    phone="9876543210",
                    full_name="Rajendra Prasad Sharma",
                    hashed_password=get_password_hash("officer123"),
                    role="LAND_RECORD_OFFICER",
                    department="Department of Land Resources (DoLR)",
                    designation="Senior Revenue Officer & Tahsildar",
                    is_active=True
                ),
                User(
                    username="admin",
                    email="admin@dolr.gov.in",
                    phone="9876543211",
                    full_name="Dr. Sunita Deshmukh",
                    hashed_password=get_password_hash("admin123"),
                    role="ADMIN",
                    department="Ministry of Rural Development",
                    designation="National Portal Administrator",
                    is_active=True
                ),
                User(
                    username="citizen",
                    email="citizen@india.gov.in",
                    phone="9876543212",
                    full_name="Aditya Verma",
                    hashed_password=get_password_hash("citizen123"),
                    role="CITIZEN",
                    department="Citizen Portal",
                    designation="Public Citizen",
                    is_active=True
                )
            ]
            db.add_all(users)
            db.commit()
            print("Seeded demo users.")

        # 4. Seed Cadastral Ground Truth Database
        if db.query(CadastralRecord).count() == 0:
            cadastral_data = [
                CadastralRecord(
                    survey_number="123/4A",
                    village="Rampur Kalan",
                    district="Bhopal",
                    cadastral_area=2.40,  # Deliberate 0.05 Ac delta against incoming 2.45 Ac
                    survey_year=2021,
                    coordinates_geojson={
                        "type": "Polygon",
                        "coordinates": [[[77.4126, 23.2599], [77.4150, 23.2599], [77.4150, 23.2575], [77.4126, 23.2575], [77.4126, 23.2599]]]
                    }
                ),
                CadastralRecord(
                    survey_number="101/2B",
                    village="Rampur Kalan",
                    district="Bhopal",
                    cadastral_area=1.80,
                    survey_year=2020,
                    coordinates_geojson={
                        "type": "Polygon",
                        "coordinates": [[[77.4160, 23.2610], [77.4185, 23.2610], [77.4185, 23.2585], [77.4160, 23.2585], [77.4160, 23.2610]]]
                    }
                ),
                CadastralRecord(
                    survey_number="105/3C",
                    village="Sanwer Dehat",
                    district="Indore",
                    cadastral_area=0.35,
                    survey_year=2022,
                    coordinates_geojson={
                        "type": "Polygon",
                        "coordinates": [[[75.8577, 22.7196], [75.8600, 22.7196], [75.8600, 22.7170], [75.8577, 22.7170], [75.8577, 22.7196]]]
                    }
                ),
                CadastralRecord(
                    survey_number="214/1",
                    village="Berasia Khurd",
                    district="Bhopal",
                    cadastral_area=1.15,
                    survey_year=2019,
                    coordinates_geojson={
                        "type": "Polygon",
                        "coordinates": [[[77.4200, 23.2700], [77.4230, 23.2700], [77.4230, 23.2670], [77.4200, 23.2670], [77.4200, 23.2700]]]
                    }
                ),
                CadastralRecord(
                    survey_number="78/A",
                    village="Shamshabad Rural",
                    district="Ranga Reddy",
                    cadastral_area=0.95,
                    survey_year=2023,
                    coordinates_geojson={
                        "type": "Polygon",
                        "coordinates": [[[78.4350, 17.2600], [78.4375, 17.2600], [78.4375, 17.2575], [78.4350, 17.2575], [78.4350, 17.2600]]]
                    }
                )
            ]
            db.add_all(cadastral_data)
            db.commit()
            print("Seeded cadastral ground truth.")

        # 5. Seed Land Records if empty
        records_path = os.path.join(sample_dir, "sample_records.json")
        if os.path.exists(records_path) and db.query(LandRecord).count() == 0:
            with open(records_path, "r", encoding="utf-8") as f:
                rec_data = json.load(f)
            for r in rec_data:
                db.add(LandRecord(**r))
            db.commit()
            print("Seeded initial approved land records.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
