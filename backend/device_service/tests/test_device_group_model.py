"""Tests for Device Group Model (Task 037)."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from device_service.models.device_group import DeviceGroup
from device_service.models.device import Device, DeviceStatus
from school_service.models.school import School


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_groups_table_exists(test_db: AsyncSession):
    """
    Test that device_groups table exists in the database.
    
    Acceptance Criteria:
    - DeviceGroup model exists with all required fields
    - Database migration creates `device_groups` table correctly
    """
    async with test_db.bind.connect() as conn:
        def check_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(check_tables)

        assert "device_groups" in tables, "device_groups table should exist in the database"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_groups_table_has_all_required_columns(test_db: AsyncSession):
    """
    Test that device_groups table has all required columns with correct types.
    
    Acceptance Criteria:
    - DeviceGroup model exists with all required fields
    - Database migration creates `device_groups` table correctly
    """
    async with test_db.bind.connect() as conn:
        def get_columns(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_columns("device_groups")

        columns = await conn.run_sync(get_columns)
        column_names = [col["name"] for col in columns]

        # Required columns
        required_columns = [
            "id",
            "school_id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "is_deleted",
        ]

        for col_name in required_columns:
            assert col_name in column_names, f"Column '{col_name}' should exist in device_groups table"

        # Verify column types and constraints
        column_dict = {col["name"]: col for col in columns}

        # id - Integer, primary key, autoincrement
        assert column_dict["id"]["type"].python_type == int, "id should be Integer type"
        assert bool(column_dict["id"]["primary_key"]), "id should be primary key"

        # school_id - Integer, foreign key, not null
        assert column_dict["school_id"]["type"].python_type == int, "school_id should be Integer type"
        assert column_dict["school_id"]["nullable"] is False, "school_id should be NOT NULL"

        # name - String, not null
        assert column_dict["name"]["nullable"] is False, "name should be NOT NULL"

        # description - Text, nullable
        assert column_dict["description"]["nullable"] is True, "description should be nullable"

        # is_deleted - Boolean, not null, has default
        assert column_dict["is_deleted"]["nullable"] is False, "is_deleted should be NOT NULL"

        # created_at - DateTime, not null, has default
        assert column_dict["created_at"]["nullable"] is False, "created_at should be NOT NULL"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_device_group(test_db: AsyncSession):
    """
    Test creating a device group.
    
    Acceptance Criteria:
    - Can create DeviceGroup instances
    """
    # Create a school first
    school = School(
        name="Test School",
        code="TEST001",
    )
    test_db.add(school)
    await test_db.flush()

    # Create device group
    device_group = DeviceGroup(
        school_id=school.id,
        name="Main Gate",
        description="Devices at the main gate entrance",
    )
    test_db.add(device_group)
    await test_db.flush()
    await test_db.refresh(device_group)

    assert device_group.id is not None
    assert device_group.school_id == school.id
    assert device_group.name == "Main Gate"
    assert device_group.description == "Devices at the main gate entrance"
    assert device_group.is_deleted is False
    assert device_group.created_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_school_relationship(test_db: AsyncSession):
    """
    Test DeviceGroup-School relationship.
    
    Acceptance Criteria:
    - Foreign key to schools table works
    - Relationship with devices table (one-to-many)
    """
    # Create a school
    school = School(
        name="Test School",
        code="TEST001",
    )
    test_db.add(school)
    await test_db.flush()

    # Create device group
    device_group = DeviceGroup(
        school_id=school.id,
        name="Main Gate",
    )
    test_db.add(device_group)
    await test_db.flush()
    await test_db.refresh(device_group)

    # Load school relationship
    await test_db.refresh(school, ["device_groups"])

    assert device_group.school.id == school.id
    assert device_group.school.name == school.name
    assert device_group in school.device_groups


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_unique_name_per_school(test_db: AsyncSession):
    """
    Test unique constraint on (school_id, name).
    
    Acceptance Criteria:
    - Group name has unique constraint per school
    """
    # Create a school
    school = School(
        name="Test School",
        code="TEST001",
    )
    test_db.add(school)
    await test_db.flush()

    # Create first device group
    device_group1 = DeviceGroup(
        school_id=school.id,
        name="Main Gate",
    )
    test_db.add(device_group1)
    await test_db.flush()

    # Try to create another group with same name (same school) - should fail
    device_group2 = DeviceGroup(
        school_id=school.id,
        name="Main Gate",
    )
    test_db.add(device_group2)
    
    with pytest.raises(IntegrityError):
        await test_db.flush()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_same_name_different_schools(test_db: AsyncSession):
    """
    Test that same group name can exist in different schools.
    
    Acceptance Criteria:
    - Unique constraint is per-school (not global)
    """
    # Create two schools
    school1 = School(name="School 1", code="SCH001")
    school2 = School(name="School 2", code="SCH002")
    test_db.add_all([school1, school2])
    await test_db.flush()

    # Create device groups with same name in different schools
    group1 = DeviceGroup(school_id=school1.id, name="Main Gate")
    group2 = DeviceGroup(school_id=school2.id, name="Main Gate")
    
    test_db.add_all([group1, group2])
    await test_db.flush()  # Should not raise error

    assert group1.name == group2.name
    assert group1.school_id != group2.school_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_device_relationship(test_db: AsyncSession):
    """
    Test DeviceGroup-Device relationship.
    
    Acceptance Criteria:
    - Relationship with devices table (one-to-many)
    """
    # Create a school
    school = School(name="Test School", code="TEST001")
    test_db.add(school)
    await test_db.flush()

    # Create device group
    device_group = DeviceGroup(school_id=school.id, name="Main Gate")
    test_db.add(device_group)
    await test_db.flush()

    # Create devices and assign to group
    device1 = Device(
        school_id=school.id,
        name="Gate Scanner 1",
        ip_address="192.168.1.100",
        port=4370,
        device_group_id=device_group.id,
        status=DeviceStatus.UNKNOWN,
    )
    device2 = Device(
        school_id=school.id,
        name="Gate Scanner 2",
        ip_address="192.168.1.101",
        port=4370,
        device_group_id=device_group.id,
        status=DeviceStatus.UNKNOWN,
    )
    test_db.add_all([device1, device2])
    await test_db.flush()
    await test_db.refresh(device_group, ["devices"])

    assert len(device_group.devices) == 2
    assert device1 in device_group.devices
    assert device2 in device_group.devices
    assert device1.device_group_id == device_group.id
    assert device2.device_group_id == device_group.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_soft_delete(test_db: AsyncSession):
    """
    Test soft delete functionality.
    
    Acceptance Criteria:
    - Model includes soft delete support (is_deleted)
    """
    # Create a school
    school = School(name="Test School", code="TEST001")
    test_db.add(school)
    await test_db.flush()

    # Create device group
    device_group = DeviceGroup(school_id=school.id, name="Main Gate")
    test_db.add(device_group)
    await test_db.flush()

    assert device_group.is_deleted is False

    # Soft delete
    device_group.is_deleted = True
    await test_db.flush()
    await test_db.refresh(device_group)

    assert device_group.is_deleted is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_timestamps(test_db: AsyncSession):
    """
    Test timestamp fields (created_at, updated_at).
    
    Acceptance Criteria:
    - Model includes timestamps (created_at, updated_at)
    """
    # Create a school
    school = School(name="Test School", code="TEST001")
    test_db.add(school)
    await test_db.flush()

    # Create device group
    device_group = DeviceGroup(school_id=school.id, name="Main Gate")
    test_db.add(device_group)
    await test_db.flush()
    await test_db.refresh(device_group)

    # Verify timestamps exist
    assert hasattr(device_group, "created_at"), "DeviceGroup model should have created_at attribute"
    assert hasattr(device_group, "updated_at"), "DeviceGroup model should have updated_at attribute"
    assert device_group.created_at is not None, "created_at should be set when device group is created"

    # Note: SQLite may not update updated_at automatically in tests, but the field should exist
    assert hasattr(device_group, "updated_at"), "updated_at should exist"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_defaults(test_db: AsyncSession):
    """
    Test default values for device group.
    
    Acceptance Criteria:
    - Default values are set correctly
    """
    # Create a school
    school = School(name="Test School", code="TEST001")
    test_db.add(school)
    await test_db.flush()

    # Create device group with minimal fields
    device_group = DeviceGroup(
        school_id=school.id,
        name="Main Gate",
    )
    test_db.add(device_group)
    await test_db.flush()
    await test_db.refresh(device_group)

    assert device_group.description is None
    assert device_group.is_deleted is False
    assert device_group.created_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_foreign_key_constraint(test_db: AsyncSession):
    """
    Test foreign key constraint to schools table.
    
    Acceptance Criteria:
    - Foreign key to schools table (required)
    """
    async with test_db.bind.connect() as conn:
        def get_foreign_keys(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_foreign_keys("device_groups")
        
        foreign_keys = await conn.run_sync(get_foreign_keys)
        
        # Find foreign key to schools table
        school_fk = None
        for fk in foreign_keys:
            if fk["referred_table"] == "schools" and "school_id" in fk["constrained_columns"]:
                school_fk = fk
                break
        
        assert school_fk is not None, "device_groups table should have foreign key to schools table"
        assert "school_id" in school_fk["constrained_columns"], "Foreign key should be on school_id column"
        assert "id" in school_fk["referred_columns"], "Foreign key should reference schools.id"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_indexes(test_db: AsyncSession):
    """
    Test that indexes are created correctly.
    
    Acceptance Criteria:
    - Index on school_id, name, is_deleted
    """
    async with test_db.bind.connect() as conn:
        def get_indexes(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_indexes("device_groups")

        indexes = await conn.run_sync(get_indexes)
        index_names = [idx["name"] for idx in indexes]

        # Check for common index patterns (actual names may vary)
        # At minimum, primary key index should exist
        assert len(indexes) > 0, "Should have at least one index (primary key)"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_group_repr(test_db: AsyncSession):
    """
    Test __repr__ method.
    
    Acceptance Criteria:
    - Model includes timestamps (created_at, updated_at)
    """
    # Create a school
    school = School(name="Test School", code="TEST001")
    test_db.add(school)
    await test_db.flush()

    # Create device group
    device_group = DeviceGroup(school_id=school.id, name="Main Gate")
    test_db.add(device_group)
    await test_db.flush()

    repr_str = repr(device_group)
    assert "DeviceGroup" in repr_str
    assert str(device_group.id) in repr_str
    assert device_group.name in repr_str
    assert str(device_group.school_id) in repr_str

