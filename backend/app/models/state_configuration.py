from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class StateConfiguration(Base):
    __tablename__ = 'state_configurations'

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey('states.id'), unique=True, nullable=False)
    survey_number_label = Column(String(100), default='Survey Number')  # e.g., Survey Number, Khasra Number, Dag Number
    admin_unit_label = Column(String(100), default='Tehsil')  # Tehsil, Mandal, Taluka, Block, Circle
    default_area_unit = Column(String(50), default='Acres')  # Acres, Hectares, Bigha, Guntha
    language_code = Column(String(20), default='en')  # en, hi, te, ta, mr
    validation_rules_json = Column(JSON, nullable=True)

    state = relationship('State', back_populates='configurations')
