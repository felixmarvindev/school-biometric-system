"""Pydantic schemas for Device Group."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DeviceGroupBase(BaseModel):
    """Base schema with common device group fields."""

    name: str = Field(..., min_length=1, max_length=200, description="Group name")
    description: Optional[str] = Field(None, description="Group description")


class DeviceGroupCreate(DeviceGroupBase):
    """Schema for creating a new device group."""

    pass


class DeviceGroupUpdate(BaseModel):
    """Schema for updating device group (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Group name")
    description: Optional[str] = Field(None, description="Group description")


class DeviceGroupResponse(DeviceGroupBase):
    """Schema for device group response."""

    id: int
    school_id: int
    device_count: int = 0  # Number of devices in group
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceGroupListResponse(BaseModel):
    """Paginated list of device groups."""

    items: List[DeviceGroupResponse]
    total: int
    page: int
    page_size: int
    pages: int

