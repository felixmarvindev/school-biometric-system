# Task 014: Student Pydantic Schemas

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 1: Student Data Model

## Description

Create Pydantic schemas for student data validation, request/response models, and API serialization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] StudentBase schema exists with common fields
2. [ ] StudentCreate schema exists for creation
3. [ ] StudentUpdate schema exists for updates
4. [ ] StudentResponse schema exists for API responses
5. [ ] ClassBase, ClassCreate, ClassResponse schemas exist
6. [ ] StreamBase, StreamCreate, StreamResponse schemas exist
7. [ ] All schemas have proper validation
8. [ ] Schemas exclude sensitive/internal fields from responses

## Technical Details

### Files to Create/Modify

```
backend/shared/schemas/student.py
backend/shared/schemas/class.py
backend/shared/schemas/stream.py
```

### Key Code Patterns

```python
# schemas/student.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
from typing import Optional
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class StudentBase(BaseModel):
    """Base schema for Student with common fields."""
    admission_number: str = Field(..., min_length=1, max_length=50, description="Unique admission number per school")
    first_name: str = Field(..., min_length=1, max_length=100, description="Student first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Student last name")
    date_of_birth: Optional[date] = Field(None, description="Student date of birth")
    gender: Optional[Gender] = Field(None, description="Student gender")
    parent_phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$', description="Parent/guardian phone number")
    parent_email: Optional[EmailStr] = Field(None, description="Parent/guardian email address")

class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    school_id: int = Field(..., description="ID of the school")
    class_id: Optional[int] = Field(None, description="ID of the class (optional)")
    stream_id: Optional[int] = Field(None, description="ID of the stream (optional)")

class StudentUpdate(BaseModel):
    """Schema for updating student information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    parent_phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    parent_email: Optional[EmailStr] = None
    # Note: admission_number and school_id are immutable

class StudentResponse(StudentBase):
    """Schema for student response."""
    id: int
    school_id: int
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Dependencies

- Task 012 (Student model must exist)
- Task 013 (Class and Stream models must exist)

## Visual Testing

### Before State
- No Pydantic schemas for students
- Cannot validate student data

### After State
- Schemas exist for all operations
- Validation works correctly
- API can serialize/deserialize student data

### Testing Steps

1. Test StudentCreate validation
2. Test StudentUpdate validation
3. Test StudentResponse serialization
4. Verify required fields are enforced
5. Verify optional fields work correctly

## Definition of Done

- [ ] Code written and follows standards
- [ ] All schemas have proper validation
- [ ] Schemas tested with valid/invalid data
- [ ] Response schemas exclude internal fields
- [ ] Code reviewed

## Time Estimate

2-3 hours

## Notes

- Admission number validation should be per-school (handled in service layer)
- Date of birth should be in the past
- Phone validation uses same pattern as school phone
- Email validation uses EmailStr from Pydantic
- Update schema excludes immutable fields (admission_number, school_id)

