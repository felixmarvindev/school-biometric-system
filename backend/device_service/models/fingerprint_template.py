"""Fingerprint template database model."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base


class FingerprintTemplate(Base):
    """
    Model for storing fingerprint templates independently of enrollment sessions.

    Enables template transfer when a device is lost and provides a canonical store.
    """

    __tablename__ = "fingerprint_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    finger_id = Column(Integer, nullable=False, index=True)  # 0-9

    encrypted_data = Column(Text, nullable=False)
    quality_score = Column(Integer, nullable=True)  # 0-100

    source_enrollment_session_id = Column(
        Integer,
        ForeignKey("enrollment_sessions.id"),
        nullable=True,
        index=True,
    )

    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)

    # Relationships
    student = relationship("Student", lazy="selectin")
    device = relationship("Device", lazy="selectin")
    school = relationship("School", lazy="selectin")
    source_enrollment_session = relationship(
        "EnrollmentSession",
        foreign_keys=[source_enrollment_session_id],
        lazy="selectin",
    )

    __table_args__ = (
        {"comment": "Canonical fingerprint template store for transfer/recovery"},
    )

    def __repr__(self) -> str:
        return (
            f"<FingerprintTemplate(id={self.id}, student_id={self.student_id}, "
            f"device_id={self.device_id}, finger_id={self.finger_id})>"
        )
