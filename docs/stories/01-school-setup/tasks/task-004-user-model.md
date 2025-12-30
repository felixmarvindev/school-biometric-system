# Task 004: User Model and Authentication

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 2: Admin User Creation

## Description

Create the User database model with school association, password hashing, and authentication setup (JWT).

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] User model exists with all required fields
2. [x] Database migration creates `users` table correctly
3. [x] User has foreign key to schools table
4. [x] Password is hashed using bcrypt/passlib
5. [x] Password strength validation implemented
6. [x] JWT token generation works
7. [x] JWT token validation works
8. [x] Login endpoint exists
9. [x] User creation during registration works (combined with school in atomic transaction)
10. [x] `create_user_without_commit()` method implemented for transaction support
11. [x] Transaction rollback implemented if user creation fails

## Technical Details

### Files to Create/Modify

```
backend/school_service/models/user.py
backend/school_service/core/security.py
backend/school_service/api/routes/auth.py
backend/school_service/services/user_service.py (create_user, create_user_without_commit)
backend/school_service/repositories/user_repository.py (create_user, create_user_without_commit)
backend/alembic/versions/XXXX_create_users_table.py
```

### Key Code Patterns

```python
# models/user.py
from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    school_id = Column(BigInteger, ForeignKey("schools.id"), nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), default="school_admin", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    school = relationship("School", back_populates="users")

# core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # JWT token creation
    pass
```

### Dependencies

- Task 001 (School model must exist)
- python-jose installed
- passlib[bcrypt] installed
- SECRET_KEY configured in environment

## Visual Testing

### Before State
- No users table in database
- No authentication system

### After State
- Users table exists
- Can create users with hashed passwords
- Can generate and validate JWT tokens
- Login endpoint works

### Testing Steps

1. Run migration - verify users table created
2. Create user - verify password is hashed
3. Generate JWT token - verify token format
4. Validate token - verify token validation works
5. Test login endpoint - verify returns token

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Password hashing verified (not plain text)
- [x] JWT tokens work correctly
- [x] Migration runs successfully
- [x] Code reviewed
- [x] Security best practices followed

## Time Estimate

8-10 hours

## Notes

- Never store passwords in plain text
- Use strong password hashing (bcrypt recommended)
- JWT tokens should have expiration
- Consider refresh tokens for better security
- Log authentication attempts for security
- **Transaction Support**: `create_user_without_commit()` allows user creation as part of larger transactions
- **Atomic Operations**: User creation during registration is part of atomic transaction with school creation
- **Rollback**: If user creation fails, school creation is automatically rolled back

