from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.app.core.database import Base

class AICorrection(Base):
    __tablename__ = 'ai_corrections'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=True)
    field_name = Column(String(100), nullable=False)
    original_ai_value = Column(String(255), nullable=False)
    corrected_value = Column(String(255), nullable=False)
    officer_id = Column(Integer, nullable=True)
    officer_name = Column(String(150), default='Officer')
    reason = Column(String(255), nullable=True)  # e.g. 'OCR digit error', 'Ambiguous character', 'Manual update'
    language = Column(String(50), default='English')
    document_type = Column(String(100), default='Registered Sale Deed')
    timestamp = Column(DateTime, default=datetime.utcnow)
