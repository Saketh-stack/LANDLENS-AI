from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, create_access_token
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserInfoOut
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "127.0.0.1"
    return AuthService.authenticate_user(req, db, ip_address=ip)

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.register_user(req, db)
    return {
        "message": f"User {user.username} registered successfully.",
        "user_id": user.id,
        "role": user.role
    }

@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    new_token = create_access_token(data={"sub": current_user.username, "role": current_user.role})
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserInfoOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
