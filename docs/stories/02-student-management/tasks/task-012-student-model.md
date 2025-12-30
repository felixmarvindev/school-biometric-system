# Task 012: Student Database Model

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 1: Student Data Model

## Description

Create the Student database model with all required fields, relationships, and database migration.

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Student model exists with all required fields
2. [x] Database migration creates `students` table correctly
3. [x] Admission number has unique constraint per school
4. [x] Model includes timestamps (created_at, updated_at)
5. [x] Model includes soft delete support (is_deleted)
6. [x] Foreign key to schools table
7. [x] Foreign key to classes table (optional, nullable)
8. [x] Foreign key to streams table (optional, nullable)
9. [x] Migration runs successfully without errors

## Technical Details

### Files to Create/Modify

```
backend/school_service/models/student.py
backend/shared/schemas/student.py
backend/alembic/versions/XXXX_create_students_table.py
```

### Key Code Patterns

```python
# models/student.py
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base
import enum

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    admission_number = Column(String(50), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True, index=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=True, index=True)
    
    # Parent contact information
    parent_phone = Column(String(20), nullable=True)
    parent_email = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)
    
    # Relationships
    school = relationship("School", back_populates="students")
    class_ = relationship("Class", back_populates="students")
    stream = relationship("Stream", back_populates="students")
    
    # Unique constraint: admission_number must be unique per school
    __table_args__ = (
        {"comment": "Students enrolled in schools"}
    )
```

### Database Constraints

- Unique constraint on `(school_id, admission_number)` - admission numbers must be unique per school
- Foreign key to `schools.id` (required)
- Foreign key to `classes.id` (optional, nullable)
- Foreign key to `streams.id` (optional, nullable)
- Index on `school_id`, `admission_number`, `class_id`, `stream_id`, `is_deleted`

### Dependencies

- Task 001 (School model must exist)
- Alembic migrations configured

## Visual Testing

### Before State
- No students table exists
- Cannot store student data

### After State
- Students table exists
- Can create Student instances
- Relationships work correctly

### Testing Steps

1. Run migration - verify table created
2. Create test student - verify all fields work
3. Test relationships - verify foreign keys work
4. Test unique constraint - verify admission_number uniqueness per school

## Definition of Done

- [x] Code written and follows standards
- [x] Migration script created and tested
- [x] Model relationships verified
- [x] Unique constraints tested
- [x] Foreign keys tested
- [x] Comprehensive tests written and passing (10 tests)
- [x] Migration applied to test database

## Time Estimate

4-6 hours

## Notes

- Admission number format: typically "STD-001", "2024-001", etc. (school-specific)
- Date of birth is optional (some schools may not have this)
- Gender is optional (privacy considerations)
- Parent contact info is optional but recommended for notifications
- Class and stream assignment can be done later (Phase 3)

