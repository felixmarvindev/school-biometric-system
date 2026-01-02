"""Device Group database model."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base


class DeviceGroup(Base):
    """Device Group model for organizing biometric devices."""

    __tablename__ = "device_groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)

    # Relationships
    school = relationship("School", back_populates="device_groups", lazy="selectin")
    devices = relationship("Device", back_populates="device_group", lazy="selectin")

    # Unique constraint: name must be unique per school
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_device_groups_school_name"),
        {"comment": "Device groups for organizing biometric devices"},
    )

    def __repr__(self) -> str:
        return f"<DeviceGroup(id={self.id}, name='{self.name}', school_id={self.school_id})>"

