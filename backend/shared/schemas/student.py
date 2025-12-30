"""Pydantic schemas for Student."""

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum

from school_service.models.student import Gender as ModelGender


class Gender(str, Enum):
    """Gender enumeration for Pydantic validation."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentBase(BaseModel):
    """Base schema for Student with common fields."""

    admission_number: str = Field(
        ..., min_length=1, max_length=50, description="Unique admission number per school"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Student first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Student last name")
    date_of_birth: Optional[date] = Field(None, description="Student date of birth")
    gender: Optional[Gender] = Field(None, description="Student gender")
    parent_phone: Optional[str] = Field(
        None, pattern=r"^\+?[0-9]{10,15}$", description="Parent/guardian phone number"
    )
    parent_email: Optional[EmailStr] = Field(None, description="Parent/guardian email address")


class StudentCreate(StudentBase):
    """Schema for creating a new student."""

    school_id: int = Field(..., description="ID of the school")
    class_id: Optional[int] = Field(None, description="ID of the class (optional)")
    stream_id: Optional[int] = Field(None, description="ID of the stream (optional)")


class StudentUpdate(BaseModel):
    """Schema for updating student information."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    parent_phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    parent_email: Optional[EmailStr] = None
    # Note: admission_number and school_id are immutable


class StudentResponse(StudentBase):
    """Schema for student response."""

    id: int
    school_id: int
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

