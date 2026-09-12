from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import  get_db
from backend.app.models import  User, AuditLog
from backend.app.auth_util import  verify_password, hash_password
from backend.app.auth import  create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "CITIZEN"

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == req.username) | (User.email == req.username)
    ).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your username and password."
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    # Audit log
    audit = AuditLog(
        actor=user.full_name,
        actor_role=user.role,
        action="USER_LOGIN",
        entity_type="SYSTEM",
        entity_id=str(user.id),
        details=f"User {user.username} logged into {user.role} workspace"
    )
    db.add(audit)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "designation": user.designation
        }
    }

@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
        "designation": current_user.designation
    }
