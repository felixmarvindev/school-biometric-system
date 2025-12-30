"""Pydantic schemas for Stream."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StreamBase(BaseModel):
    """Base schema for Stream with common fields."""

    name: str = Field(..., min_length=1, max_length=50, description="Stream name (e.g., A, B, C)")
    description: Optional[str] = Field(None, max_length=500, description="Stream description")


class StreamCreate(StreamBase):
    """Schema for creating a new stream."""

    class_id: int = Field(..., description="ID of the class")


class StreamUpdate(BaseModel):
    """Schema for updating stream information."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    # Note: class_id is immutable


class StreamResponse(StreamBase):
    """Schema for stream response."""

    id: int
    class_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

