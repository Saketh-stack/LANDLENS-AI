from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict

class DashboardCardsOut(BaseModel):
    total_land_records: int
    digitized: int
    pending_verification: int
    approved_records: int
    rejected_records: int
    low_confidence_records: int
    validation_errors: int
    new_registrations: int
    average_ocr_accuracy: str
    target_processing_time: str
    model_config = ConfigDict(from_attributes=True)

class DashboardMetricsOut(BaseModel):
    cards: DashboardCardsOut
    charts: Dict[str, Any]
    recent_activity: Optional[List[Dict[str, Any]]] = []
    model_config = ConfigDict(from_attributes=True)
