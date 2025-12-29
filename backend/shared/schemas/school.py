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

