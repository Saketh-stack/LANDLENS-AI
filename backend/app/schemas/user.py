from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str = "CITIZEN"
    department: Optional[str] = None
    designation: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

