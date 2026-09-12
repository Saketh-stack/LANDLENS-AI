from sqlalchemy import Column, Integer, String, Float, JSON
from backend.app.core.database import Base

class CadastralRecord(Base):
    __tablename__ = 'cadastral_records'

    id = Column(Integer, primary_key=True, index=True)
    survey_number = Column(String(100), unique=True, index=True, nullable=False)
    village = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    cadastral_area = Column(Float, nullable=False)
    survey_year = Column(Integer, default=2021)
    geometry_type = Column(String(50), default='Polygon')
    coordinates_geojson = Column(JSON, nullable=True)
