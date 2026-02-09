# Task 065: Enrollment Session Model

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 2: Device Control

## Description

Create the database model and schema for enrollment sessions to track enrollment state, progress, and results.

## Type
- [ ] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
0.5 day

## Prerequisites

- ✅ Phase 1 complete (enrollment UI ready)
- ✅ Database migrations working (Alembic)

## Acceptance Criteria

1. [x] Enrollment session model created
2. [x] Model includes: student_id, device_id, finger_id, status, session_id
3. [x] Model includes: started_at, completed_at, error_message
4. [x] Model includes: template_data (encrypted, nullable)
5. [x] Model includes: quality_score (nullable)
6. [x] Database migration created
7. [x] Model relationships defined (student, device)
8. [x] Soft delete support (is_deleted)

## Implementation Details

### Backend Changes

1. **backend/device_service/models/enrollment.py**
   - Create EnrollmentSession model
   - Add all required fields
   - Add relationships
   - Add indexes

2. **backend/shared/schemas/enrollment.py**
   - Create EnrollmentSessionCreate schema
   - Create EnrollmentSessionResponse schema
   - Create EnrollmentSessionUpdate schema

3. **Database Migration**
   - Run `alembic revision --autogenerate -m "add_enrollment_sessions"`
   - Review and apply migration

### Key Code Patterns

```python
# backend/device_service/models/enrollment.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import enum

class EnrollmentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EnrollmentSession(Base):
    """Model for tracking enrollment sessions."""
    
    __tablename__ = "enrollment_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    finger_id = Column(Integer, nullable=False)  # 0-9
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    
    status = Column(String(20), server_default=text("'pending'"), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Template data (encrypted before storage)
    template_data = Column(Text, nullable=True)  # Encrypted fingerprint template
    quality_score = Column(Integer, nullable=True)  # 0-100
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)
    
    # Relationships
    student = relationship("Student", back_populates="enrollment_sessions")
    device = relationship("Device", back_populates="enrollment_sessions")
    school = relationship("School")
```

## Testing

### Manual Testing

1. **Database Migration**
   - Run migration
   - ✅ Verify table created
   - ✅ Verify all columns exist
   - ✅ Verify indexes created

2. **Model Creation**
   - Create enrollment session in code
   - ✅ Verify can save to database
   - ✅ Verify relationships work

## Definition of Done

- [x] Enrollment session model created
- [x] All required fields included
- [x] Database migration created and applied
- [x] Model relationships work
- [x] Soft delete support added

## Next Task

**Task 066: Enrollment Command Handler** - Implement device enrollment command sending.
