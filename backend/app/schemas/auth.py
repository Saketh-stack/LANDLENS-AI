from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    phone: Optional[str] = None
    role: str = "CITIZEN"
    department: Optional[str] = "Citizen Portal"
    designation: Optional[str] = "Public Citizen"

class UserInfoOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    designation: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfoOut
