from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class AdministrativeUnit(Base):
    __tablename__ = 'administrative_units'

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=False)
    name = Column(String(100), nullable=False)
    unit_type = Column(String(50), default='Tehsil')  # Tehsil, Mandal, Taluka, Block, Sub-Division

    district = relationship('District', back_populates='administrative_units')
    villages = relationship('Village', back_populates='administrative_unit', cascade='all, delete-orphan')
