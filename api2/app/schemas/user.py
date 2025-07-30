from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    name: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = "USER"
    provider: Optional[str] = "local"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserResponse 