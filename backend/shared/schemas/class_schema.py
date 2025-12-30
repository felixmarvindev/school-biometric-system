"""Pydantic schemas for Class."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ClassBase(BaseModel):
    """Base schema for Class with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Class name (e.g., Form 1, Grade 3)")
    description: Optional[str] = Field(None, max_length=500, description="Class description")


class ClassCreate(ClassBase):
    """Schema for creating a new class."""

    school_id: Optional[int] = Field(None, description="ID of the school (auto-assigned from authenticated user)")


class ClassUpdate(BaseModel):
    """Schema for updating class information."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    # Note: school_id is immutable


class ClassResponse(ClassBase):
    """Schema for class response."""

    id: int
    school_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

