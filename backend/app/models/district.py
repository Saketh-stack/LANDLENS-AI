from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class District(Base):
    __tablename__ = 'districts'

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey('states.id'), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)

    state = relationship('State', back_populates='districts')
    administrative_units = relationship('AdministrativeUnit', back_populates='district', cascade='all, delete-orphan')
