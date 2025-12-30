"""Pydantic schemas for School."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class SchoolBase(BaseModel):
    """Base schema for School with common fields."""

    name: str = Field(..., min_length=1, max_length=200, description="School name")
    code: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9-]+$",
        description="Unique school code (letters, numbers, and hyphens only - will be normalized to uppercase)",
    )

    @field_validator("code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        """Normalize school code to uppercase."""
        return v.upper()
    address: Optional[str] = Field(None, max_length=500, description="School address")
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+?[0-9]{10,15}$",
        description="School phone number",
    )
    email: Optional[EmailStr] = Field(None, description="School email address")


class SchoolCreate(SchoolBase):
    """Schema for creating a new school."""

    pass


class SchoolUpdate(BaseModel):
    """Schema for updating school information (code is immutable)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    email: Optional[EmailStr] = None


class SchoolResponse(SchoolBase):
    """Schema for school response."""

    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminUserDetails(BaseModel):
    """Schema for admin user details during school registration."""

    email: EmailStr = Field(..., description="Admin email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Admin first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Admin last name")
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Admin password (must be at least 8 characters and no more than 72 bytes with uppercase, lowercase, digit, and special character)"
    )


class SchoolRegistrationWithAdmin(SchoolBase):
    """Schema for school registration with admin user creation."""

    admin: AdminUserDetails = Field(..., description="Admin user details for the school")


class SchoolRegistrationResponse(SchoolResponse):
    """Schema for school registration response including admin user info."""

    admin_user: dict = Field(..., description="Created admin user information (without password)")

