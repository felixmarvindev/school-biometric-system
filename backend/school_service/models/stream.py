"""Stream database model."""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base


class Stream(Base):
    """Stream model representing a stream within a class (e.g., A, B, C)."""

    __tablename__ = "streams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)  # e.g., "A", "B", "C"
    description = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)

    # Relationships
    class_ = relationship("AcademicClass", back_populates="streams", lazy="selectin")
    students = relationship("Student", back_populates="stream", lazy="selectin")

    # Unique constraint: stream name must be unique per class
    __table_args__ = (
        UniqueConstraint("class_id", "name", name="uq_streams_class_name"),
        {"comment": "Streams within classes (e.g., A, B, C)"},
    )

    def __repr__(self) -> str:
        return f"<Stream(id={self.id}, name='{self.name}', class_id={self.class_id})>"

