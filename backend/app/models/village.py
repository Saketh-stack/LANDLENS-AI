from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Village(Base):
    __tablename__ = 'villages'

    id = Column(Integer, primary_key=True, index=True)
    administrative_unit_id = Column(Integer, ForeignKey('administrative_units.id'), nullable=False)
    name = Column(String(100), nullable=False)
    census_code = Column(String(50), nullable=True)
    pin_code = Column(String(10), nullable=True)

    administrative_unit = relationship('AdministrativeUnit', back_populates='villages')
