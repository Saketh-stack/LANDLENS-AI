from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.user import UserOut, UserUpdate
from backend.app.models.user import User

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(current_user, k, v)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/list", response_model=List[UserOut], dependencies=[Depends(require_roles(["ADMIN"]))])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
