from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.app.core.database import Base

class Owner(Base):
    __tablename__ = 'owners'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), index=True, nullable=False)
    father_husband_name = Column(String(200), nullable=True)
    id_type = Column(String(50), default='AADHAAR')  # AADHAAR, PAN, VOTER_ID
    id_number_masked = Column(String(50), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
