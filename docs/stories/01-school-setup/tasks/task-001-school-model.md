# Task 001: School Database Model

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 1: School Registration

## Description

Create the School database model with all required fields, relationships, and database migration.

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] School model exists with all required fields
2. [x] Database migration creates `schools` table correctly
3. [x] School code has unique constraint
4. [x] Model includes timestamps (created_at, updated_at)
5. [x] Model includes soft delete support (is_deleted)
6. [x] Migration runs successfully without errors

## Technical Details

### Files to Create/Modify

```
backend/school_service/models/school.py
backend/school_service/migrations/versions/XXXX_create_schools_table.py
backend/shared/schemas/school.py
```

### Key Code Patterns

```python
# models/school.py
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.shared.database import Base

class School(Base):
    __tablename__ = "schools"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="school")
```

### Dependencies

- SQLAlchemy 2.0 installed
- Database connection configured
- Alembic migrations set up

## Visual Testing

### Before State
- No `schools` table in database
- No School model exists

### After State
- `schools` table exists in database
- Can query School model
- Database schema shows all columns with correct types

### Testing Steps

1. Run migration: `alembic upgrade head`
2. Verify table exists: Check database schema
3. Create test school: Use SQLAlchemy session to create School instance
4. Verify unique constraint: Try to create duplicate code, expect error
5. Verify timestamps: Check created_at is set automatically

## Definition of Done

- [x] Code written and follows standards
- [ ] Unit tests written and passing
- [x] Migration runs successfully
- [x] Database schema verified
- [ ] Code reviewed
- [x] Documentation updated

## Time Estimate

4-6 hours

## Notes

- Ensure school code is truly unique (database constraint)
- Consider adding index on school code for faster lookups
- Soft delete allows data retention for audits
- Timestamps help with debugging and reporting

