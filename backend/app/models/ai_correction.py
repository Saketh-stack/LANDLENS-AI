from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.app.core.database import Base

class AICorrection(Base):
    __tablename__ = 'ai_corrections'

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(100), nullable=False)
    original_ai_value = Column(String(255), nullable=False)
    corrected_value = Column(String(255), nullable=False)
    officer_name = Column(String(150), default='Officer')
    document_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
