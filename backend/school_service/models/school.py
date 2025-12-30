"""School database model."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.database.base import Base


class School(Base):
    """School model representing a registered school in the system."""

    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    # Relationships
    users = relationship("User", back_populates="school", lazy="selectin")
    classes = relationship("AcademicClass", back_populates="school", lazy="selectin")
    students = relationship("Student", back_populates="school", lazy="selectin")

    def __repr__(self) -> str:
        return f"<School(id={self.id}, name='{self.name}', code='{self.code}')>"

