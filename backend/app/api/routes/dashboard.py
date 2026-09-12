from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.dashboard import DashboardMetricsOut
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/metrics", response_model=DashboardMetricsOut)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    return DashboardService.get_metrics(db)

@router.get("/analytics")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    return DashboardService.get_metrics(db)
