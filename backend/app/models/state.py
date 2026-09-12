from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class State(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    capital = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)

    districts = relationship('District', back_populates='state', cascade='all, delete-orphan')
    configurations = relationship('StateConfiguration', back_populates='state', uselist=False, cascade='all, delete-orphan')
