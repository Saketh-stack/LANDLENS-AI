from datetime import datetime, timedelta, timezone
from typing import Optional, List, Any
import hashlib
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db

security_bearer = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    # Check bcrypt format
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False
    # Check fallback SHA256-salt
    salt = "sih2026_dolr_salt"
    sha_hash = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
    if sha_hash == hashed_password:
        return True
    return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Any:
    from backend.app.models.user import User

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Authorization header missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter((User.username == username) | (User.email == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: Any = Depends(get_current_user)):
        user_role = (current_user.role or "").upper()
        allowed = [r.upper() for r in allowed_roles]
        if user_role == "OFFICER" and "LAND_RECORD_OFFICER" in allowed:
            return current_user
        if user_role == "LAND_RECORD_OFFICER" and "OFFICER" in allowed:
            return current_user
        if user_role not in allowed and "ADMIN" not in [user_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker
