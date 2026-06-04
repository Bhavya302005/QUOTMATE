from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# Request Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2, max_length=100)
    company_name: Optional[str] = Field(None, max_length=100)
    phone: str = Field(..., max_length=15)
    gst_number: Optional[str] = Field(None, max_length=15)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Profile fields updatable via PUT /profile. Logo is only changed via POST /upload-logo."""

    email: Optional[EmailStr] = Field(None)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    company_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=500)
    gst_number: Optional[str] = Field(None, max_length=15)
    default_terms_conditions: Optional[str] = Field(None, max_length=2000)
    
    @validator('gst_number')
    def validate_gst(cls, v):
        if v and len(v) != 15:
            raise ValueError('GST number must be 15 characters')
        return v


# Response Schemas
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    company_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    gst_number: Optional[str]
    company_logo_url: Optional[str]
    default_terms_conditions: Optional[str]
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    user_id: str
    message: str
    email: str
