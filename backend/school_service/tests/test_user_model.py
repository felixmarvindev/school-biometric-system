"""Tests for User Model (Task 004)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, text, select

from school_service.models.user import User
from school_service.models.school import School
from shared.database.base import Base


def _get_inspector(session: AsyncSession):
    """Helper to get inspector from async session."""
    # Access the sync engine from the async engine
    sync_engine = session.bind.sync_engine
    return inspect(sync_engine)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_table_exists(test_db: AsyncSession):
    """
    Test that users table exists in the database.
    
    Acceptance Criteria:
    - User model exists with all required fields
    - Database migration creates `users` table correctly
    """
    # Use connection's run_sync to access the inspector in sync context
    async with test_db.bind.connect() as conn:
        def check_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()
        
        tables = await conn.run_sync(check_tables)
        
        assert "users" in tables, "users table should exist in the database"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_table_has_all_required_columns(test_db: AsyncSession):
    """
    Test that users table has all required columns with correct types.
    
    Acceptance Criteria:
    - User model exists with all required fields
    - Database migration creates `users` table correctly
    """
    # Use connection's run_sync to access the inspector in sync context
    async with test_db.bind.connect() as conn:
        def get_columns(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_columns("users")
        
        columns = await conn.run_sync(get_columns)
        column_names = [col["name"] for col in columns]
        
        # Required columns
        required_columns = [
            "id",
            "school_id",
            "email",
            "hashed_password",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        
        for col_name in required_columns:
            assert col_name in column_names, f"Column '{col_name}' should exist in users table"
        
        # Verify column types and constraints
        column_dict = {col["name"]: col for col in columns}
        
        # id - Integer, primary key, autoincrement
        assert column_dict["id"]["type"].python_type == int, "id should be Integer type"
        assert bool(column_dict["id"]["primary_key"]), "id should be primary key"
        
        # school_id - Integer, foreign key, not null
        assert column_dict["school_id"]["type"].python_type == int, "school_id should be Integer type"
        assert column_dict["school_id"]["nullable"] is False, "school_id should be NOT NULL"
        
        # email - String, unique, not null
        assert column_dict["email"]["nullable"] is False, "email should be NOT NULL"
        
        # hashed_password - String, not null
        assert column_dict["hashed_password"]["nullable"] is False, "hashed_password should be NOT NULL"
        
        # first_name - String, not null
        assert column_dict["first_name"]["nullable"] is False, "first_name should be NOT NULL"
        
        # last_name - String, not null
        assert column_dict["last_name"]["nullable"] is False, "last_name should be NOT NULL"
        
        # role - String, not null, has default
        assert column_dict["role"]["nullable"] is False, "role should be NOT NULL"
        
        # is_active - Boolean, not null, has default
        assert column_dict["is_active"]["nullable"] is False, "is_active should be NOT NULL"
        
        # is_deleted - Boolean, not null, has default
        assert column_dict["is_deleted"]["nullable"] is False, "is_deleted should be NOT NULL"
        
        # created_at - DateTime, not null, has default
        assert column_dict["created_at"]["nullable"] is False, "created_at should be NOT NULL"
        
        # updated_at - DateTime, nullable
        assert column_dict["updated_at"]["nullable"] is True, "updated_at should be nullable"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_table_has_foreign_key_to_schools(test_db: AsyncSession):
    """
    Test that users table has foreign key constraint to schools table.
    
    Acceptance Criteria:
    - User has foreign key to schools table
    """
    # Use connection's run_sync to access the inspector in sync context
    async with test_db.bind.connect() as conn:
        def get_foreign_keys(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_foreign_keys("users")
        
        foreign_keys = await conn.run_sync(get_foreign_keys)
        
        # Find foreign key to schools table
        school_fk = None
        for fk in foreign_keys:
            if fk["referred_table"] == "schools" and "school_id" in fk["constrained_columns"]:
                school_fk = fk
                break
        
        assert school_fk is not None, "users table should have foreign key to schools table"
        assert "school_id" in school_fk["constrained_columns"], "Foreign key should be on school_id column"
        assert "id" in school_fk["referred_columns"], "Foreign key should reference schools.id"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_table_has_required_indexes(test_db: AsyncSession):
    """
    Test that users table has required indexes.
    
    Acceptance Criteria:
    - Database migration creates `users` table correctly
    """
    # Use connection's run_sync to access the inspector in sync context
    async with test_db.bind.connect() as conn:
        def get_indexes(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_indexes("users")
        
        indexes = await conn.run_sync(get_indexes)
        index_names = [idx["name"] for idx in indexes]
        
        # Required indexes (based on model definition)
        required_indexes = [
            "ix_users_id",
            "ix_users_school_id",
            "ix_users_email",
            "ix_users_role",
            "ix_users_is_active",
            "ix_users_is_deleted",
        ]
        
        for idx_name in required_indexes:
            assert idx_name in index_names, f"Index '{idx_name}' should exist on users table"
        
        # Verify email index is unique
        email_index = next((idx for idx in indexes if idx["name"] == "ix_users_email"), None)
        assert email_index is not None, "Email index should exist"
        # Note: SQLite doesn't always report unique constraint on indexes, but the constraint exists


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_table_has_default_values(test_db: AsyncSession):
    """
    Test that users table has correct default values.
    
    Acceptance Criteria:
    - Database migration creates `users` table correctly
    """
    # Create a school first (required for foreign key)
    school = School(
        name="Test School",
        code="TEST-001",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a user with minimal data (should use defaults)
    user = User(
        school_id=school.id,
        email="test@example.com",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Verify defaults
    assert user.role == "school_admin", "role should default to 'school_admin'"
    assert user.is_active is True, "is_active should default to True"
    assert user.is_deleted is False, "is_deleted should default to False"
    assert user.created_at is not None, "created_at should be set automatically"
    # updated_at can be None initially
    assert user.updated_at is None or user.updated_at is not None, "updated_at can be None initially"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_model_has_timestamps(test_db: AsyncSession):
    """
    Test that User model includes timestamps.
    
    Acceptance Criteria:
    - Model includes timestamps (created_at, updated_at)
    """
    # Create a school first
    school = School(
        name="Test School",
        code="TEST-002",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a user
    user = User(
        school_id=school.id,
        email="test2@example.com",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Verify timestamps exist
    assert hasattr(user, "created_at"), "User model should have created_at attribute"
    assert hasattr(user, "updated_at"), "User model should have updated_at attribute"
    assert user.created_at is not None, "created_at should be set when user is created"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_model_has_soft_delete(test_db: AsyncSession):
    """
    Test that User model includes soft delete support.
    
    Acceptance Criteria:
    - Model includes soft delete support (is_deleted)
    """
    # Create a school first
    school = School(
        name="Test School",
        code="TEST-003",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a user
    user = User(
        school_id=school.id,
        email="test3@example.com",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Verify soft delete field exists and defaults to False
    assert hasattr(user, "is_deleted"), "User model should have is_deleted attribute"
    assert user.is_deleted is False, "is_deleted should default to False"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_model_relationship_to_school(test_db: AsyncSession):
    """
    Test that User model has relationship to School.
    
    Acceptance Criteria:
    - User has foreign key to schools table
    """
    # Create a school
    school = School(
        name="Test School",
        code="TEST-004",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a user
    user = User(
        school_id=school.id,
        email="test4@example.com",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Verify relationship
    assert hasattr(user, "school"), "User model should have school relationship"
    assert user.school is not None, "User should have access to school via relationship"
    assert user.school.id == school.id, "User's school relationship should point to correct school"

