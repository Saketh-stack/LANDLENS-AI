from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.user import User
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.schemas.auth import LoginRequest, RegisterRequest
from backend.app.services.audit_service import AuditService

class AuthService:
    @staticmethod
    def authenticate_user(req: LoginRequest, db: Session, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
        user = db.query(User).filter(
            (User.username == req.username) | (User.email == req.username)
        ).first()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials. Please verify your username and password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated."
            )

        token = create_access_token(data={"sub": user.username, "role": user.role})

        AuditService.log_event(
            db=db,
            actor=user.full_name,
            action="USER_LOGIN",
            entity_type="SYSTEM",
            actor_role=user.role,
            entity_id=str(user.id),
            details=f"User {user.username} logged in with role {user.role}",
            ip_address=ip_address
        )

        return {
            "access_token": token,
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

    @staticmethod
    def register_user(req: RegisterRequest, db: Session) -> User:
        existing = db.query(User).filter(
            (User.username == req.username) | (User.email == req.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email is already registered."
            )

        new_user = User(
            username=req.username,
            email=req.email,
            phone=req.phone,
            full_name=req.full_name,
            hashed_password=get_password_hash(req.password),
            role=req.role.upper(),
            department=req.department or "Citizen Portal",
            designation=req.designation or "Public Citizen",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
