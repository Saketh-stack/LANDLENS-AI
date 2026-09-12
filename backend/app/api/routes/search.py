from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.land_record import LandRecordPublicOut
from backend.app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["Global Search"])

@router.get("", response_model=List[LandRecordPublicOut])
def search_records(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return SearchService.search_all_records(query_str=q, db=db, include_internal=False)
