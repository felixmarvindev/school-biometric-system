"""Pydantic schemas for User."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User last name")
    role: str = Field(default="school_admin", max_length=50, description="User role")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="User password (must be at least 8 characters and no more than 72 bytes with uppercase, lowercase, digit, and special character)"
    )
    school_id: int = Field(..., description="ID of the school this user belongs to")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check byte length (bcrypt has a 72-byte limit)
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError("Password cannot be longer than 72 bytes. Please use a shorter password.")
        
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*)")
        
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""

    id: int
    school_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""

    user_id: Optional[int] = None
    email: Optional[str] = None
    school_id: Optional[int] = None

