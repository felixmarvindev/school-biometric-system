# Task 013: Class and Stream Database Models

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 1: Student Data Model

## Description

Create the Class and Stream database models for organizing students into academic groups.

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Class model exists with all required fields
2. [ ] Stream model exists with all required fields
3. [ ] Database migrations create `classes` and `streams` tables correctly
4. [ ] Class name is unique per school
5. [ ] Stream name is unique per class
6. [ ] Models include timestamps (created_at, updated_at)
7. [ ] Models include soft delete support (is_deleted)
8. [ ] Foreign key relationships work correctly
9. [ ] Migrations run successfully without errors

## Technical Details

### Files to Create/Modify

```
backend/school_service/models/class.py
backend/school_service/models/stream.py
backend/shared/schemas/class.py
backend/shared/schemas/stream.py
backend/alembic/versions/XXXX_create_classes_streams_tables.py
```

### Key Code Patterns

```python
# models/class.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Form 1", "Grade 3"
    description = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)
    
    # Relationships
    school = relationship("School", back_populates="classes")
    streams = relationship("Stream", back_populates="class_", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="class_")
    
    # Unique constraint: class name must be unique per school
    __table_args__ = (
        {"comment": "Academic classes (e.g., Form 1, Grade 3)"}
    )

# models/stream.py
class Stream(Base):
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
    class_ = relationship("Class", back_populates="streams")
    students = relationship("Student", back_populates="stream")
    
    # Unique constraint: stream name must be unique per class
    __table_args__ = (
        {"comment": "Streams within classes (e.g., A, B, C)"}
    )
```

### Database Constraints

- Unique constraint on `(school_id, name)` for classes
- Unique constraint on `(class_id, name)` for streams
- Foreign key from `streams.class_id` to `classes.id`
- Foreign key from `classes.school_id` to `schools.id`
- Indexes on foreign keys and `is_deleted`

### Dependencies

- Task 001 (School model must exist)
- Task 012 (Student model should exist for relationships)
- Alembic migrations configured

## Visual Testing

### Before State
- No classes or streams tables exist
- Cannot organize students into academic groups

### After State
- Classes and streams tables exist
- Can create Class and Stream instances
- Relationships work correctly

### Testing Steps

1. Run migration - verify tables created
2. Create test class - verify all fields work
3. Create test stream - verify relationship to class works
4. Test unique constraints - verify name uniqueness
5. Test cascade delete - verify streams deleted when class deleted

## Definition of Done

- [ ] Code written and follows standards
- [ ] Migration script created and tested
- [ ] Model relationships verified
- [ ] Unique constraints tested
- [ ] Foreign keys tested
- [ ] Code reviewed
- [ ] Migration applied to test database

## Time Estimate

4-6 hours

## Notes

- Class names are school-specific (e.g., "Form 1", "Grade 3", "Year 7")
- Stream names are typically single letters (A, B, C) or numbers (1, 2, 3)
- Streams belong to classes (hierarchical structure)
- Soft delete preserves data history
- Cascade delete: deleting a class should soft-delete its streams

