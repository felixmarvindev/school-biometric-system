"""Class database model."""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base


class AcademicClass(Base):
    """Class model representing an academic class (e.g., Form 1, Grade 3)."""

    __tablename__ = "classes"  # Table name remains "classes" for database compatibility

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Form 1", "Grade 3"
    description = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)

    # Relationships
    school = relationship("School", back_populates="classes", lazy="selectin")
    streams = relationship("Stream", back_populates="class_", cascade="all, delete-orphan", lazy="selectin")
    students = relationship("Student", back_populates="class_", lazy="selectin")

    # Unique constraint: class name must be unique per school
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_classes_school_name"),
        {"comment": "Academic classes (e.g., Form 1, Grade 3)"},
    )

    def __repr__(self) -> str:
        return f"<AcademicClass(id={self.id}, name='{self.name}', school_id={self.school_id})>"

