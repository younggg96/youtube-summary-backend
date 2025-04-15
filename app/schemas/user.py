from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱地址", example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, description="用户名", example="testuser")
    
    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only letters, numbers, underscores, and hyphens')
        return v

class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8, 
        description="密码，至少8个字符，包含大小写字母和数字", 
        example="TestPassword123"
    )
    
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    username: str = Field(..., description="用户名", example="testuser")
    password: str = Field(..., description="密码", example="TestPassword123")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="新的邮箱地址", example="newuser@example.com")
    password: Optional[str] = Field(None, description="新的密码", example="NewPassword123")
    
    @field_validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'[0-9]', v):
                raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field(..., description="令牌类型", example="bearer")

class TokenData(BaseModel):
    username: Optional[str] = None 