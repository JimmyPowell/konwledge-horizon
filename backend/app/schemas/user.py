from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for requesting verification code
class EmailRequest(BaseModel):
    email: EmailStr

# Schema for verifying code
class CodeVerify(BaseModel):
    email: EmailStr
    code: str

# Schema for user registration
class UserCreate(BaseModel):
    session: str
    username: str
    password: str

# Schema for user login
class UserLogin(BaseModel):
    identifier: str  # Can be username or email
    password: str

# Base schema for user response
class UserBase(BaseModel):
    uuid: str
    username: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# Schema for user response
class UserResponse(UserBase):
    pass
