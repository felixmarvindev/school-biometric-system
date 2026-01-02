"""Tests for Device Group Schemas (Task 038)."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from shared.schemas.device_group import (
    DeviceGroupBase,
    DeviceGroupCreate,
    DeviceGroupUpdate,
    DeviceGroupResponse,
    DeviceGroupListResponse,
)


def test_device_group_base_schema_minimal():
    """Test DeviceGroupBase schema with minimal required fields."""
    group = DeviceGroupBase(
        name="Main Gate",
    )
    assert group.name == "Main Gate"
    assert group.description is None


def test_device_group_base_schema_with_description():
    """Test DeviceGroupBase schema with description."""
    group = DeviceGroupBase(
        name="Main Gate",
        description="Devices at the main gate entrance",
    )
    assert group.name == "Main Gate"
    assert group.description == "Devices at the main gate entrance"


def test_device_group_base_schema_name_validation_min_length():
    """Test DeviceGroupBase schema name validation (minimum length)."""
    with pytest.raises(ValidationError) as exc_info:
        DeviceGroupBase(name="")
    assert "at least 1 character" in str(exc_info.value).lower() or "min_length" in str(exc_info.value)


def test_device_group_base_schema_name_validation_max_length():
    """Test DeviceGroupBase schema name validation (maximum length)."""
    long_name = "a" * 201  # 201 characters (exceeds max of 200)
    with pytest.raises(ValidationError) as exc_info:
        DeviceGroupBase(name=long_name)
    assert "at most 200" in str(exc_info.value).lower() or "max_length" in str(exc_info.value)


def test_device_group_create_schema():
    """Test DeviceGroupCreate schema."""
    group = DeviceGroupCreate(
        name="Main Gate",
        description="Gate devices",
    )
    assert group.name == "Main Gate"
    assert group.description == "Gate devices"


def test_device_group_update_schema_all_fields():
    """Test DeviceGroupUpdate schema with all fields."""
    group = DeviceGroupUpdate(
        name="Updated Gate",
        description="Updated description",
    )
    assert group.name == "Updated Gate"
    assert group.description == "Updated description"


def test_device_group_update_schema_partial():
    """Test DeviceGroupUpdate schema with partial fields."""
    # Only update name
    group = DeviceGroupUpdate(name="Updated Gate")
    assert group.name == "Updated Gate"
    assert group.description is None

    # Only update description
    group = DeviceGroupUpdate(description="Updated description")
    assert group.name is None
    assert group.description == "Updated description"

    # Empty update
    group = DeviceGroupUpdate()
    assert group.name is None
    assert group.description is None


def test_device_group_update_schema_name_validation_min_length():
    """Test DeviceGroupUpdate schema name validation (minimum length)."""
    with pytest.raises(ValidationError):
        DeviceGroupUpdate(name="")


def test_device_group_update_schema_name_validation_max_length():
    """Test DeviceGroupUpdate schema name validation (maximum length)."""
    long_name = "a" * 201  # 201 characters
    with pytest.raises(ValidationError):
        DeviceGroupUpdate(name=long_name)


def test_device_group_response_schema():
    """Test DeviceGroupResponse schema."""
    now = datetime.utcnow()
    response = DeviceGroupResponse(
        id=1,
        school_id=5,
        name="Main Gate",
        description="Gate devices",
        device_count=3,
        created_at=now,
        updated_at=None,
    )
    assert response.id == 1
    assert response.school_id == 5
    assert response.name == "Main Gate"
    assert response.description == "Gate devices"
    assert response.device_count == 3
    assert response.created_at == now
    assert response.updated_at is None


def test_device_group_response_schema_default_device_count():
    """Test DeviceGroupResponse schema with default device_count."""
    now = datetime.utcnow()
    response = DeviceGroupResponse(
        id=1,
        school_id=5,
        name="Main Gate",
        created_at=now,
    )
    assert response.device_count == 0  # Default value


def test_device_group_response_schema_with_updated_at():
    """Test DeviceGroupResponse schema with updated_at."""
    now = datetime.utcnow()
    later = datetime.utcnow()
    response = DeviceGroupResponse(
        id=1,
        school_id=5,
        name="Main Gate",
        created_at=now,
        updated_at=later,
    )
    assert response.created_at == now
    assert response.updated_at == later


def test_device_group_list_response_schema():
    """Test DeviceGroupListResponse schema."""
    now = datetime.utcnow()
    items = [
        DeviceGroupResponse(
            id=1,
            school_id=5,
            name="Main Gate",
            created_at=now,
        ),
        DeviceGroupResponse(
            id=2,
            school_id=5,
            name="Library",
            created_at=now,
        ),
    ]
    
    list_response = DeviceGroupListResponse(
        items=items,
        total=2,
        page=1,
        page_size=50,
        pages=1,
    )
    
    assert len(list_response.items) == 2
    assert list_response.total == 2
    assert list_response.page == 1
    assert list_response.page_size == 50
    assert list_response.pages == 1


def test_device_group_list_response_schema_empty():
    """Test DeviceGroupListResponse schema with empty items."""
    list_response = DeviceGroupListResponse(
        items=[],
        total=0,
        page=1,
        page_size=50,
        pages=0,
    )
    
    assert len(list_response.items) == 0
    assert list_response.total == 0
    assert list_response.pages == 0


def test_device_group_response_from_attributes():
    """Test DeviceGroupResponse can be created from model attributes."""
    # Simulate a model instance
    class MockDeviceGroup:
        def __init__(self):
            self.id = 1
            self.school_id = 5
            self.name = "Main Gate"
            self.description = "Gate devices"
            self.created_at = datetime.utcnow()
            self.updated_at = None
    
    mock_group = MockDeviceGroup()
    
    # DeviceGroupResponse should work with from_attributes=True
    # This is tested by ensuring Config.from_attributes is True
    # Actual model conversion would be tested in integration tests
    assert DeviceGroupResponse.Config.from_attributes is True


def test_device_group_base_description_optional():
    """Test that description is optional in DeviceGroupBase."""
    # Without description
    group1 = DeviceGroupBase(name="Group 1")
    assert group1.description is None

    # With None description
    group2 = DeviceGroupBase(name="Group 2", description=None)
    assert group2.description is None

    # With description
    group3 = DeviceGroupBase(name="Group 3", description="Description")
    assert group3.description == "Description"


def test_device_group_update_description_optional():
    """Test that description can be set to None in DeviceGroupUpdate."""
    group = DeviceGroupUpdate(description=None)
    assert group.description is None


def test_device_group_response_required_fields():
    """Test DeviceGroupResponse required fields."""
    now = datetime.utcnow()
    
    # Minimal required fields
    response = DeviceGroupResponse(
        id=1,
        school_id=5,
        name="Main Gate",
        created_at=now,
    )
    assert response.id == 1
    assert response.school_id == 5
    assert response.name == "Main Gate"
    assert response.device_count == 0  # Default
    assert response.description is None  # Optional


def test_device_group_schemas_type_hints():
    """Test that schemas have proper type hints."""
    # This is a basic test to ensure type hints work
    from typing import get_type_hints
    
    hints = get_type_hints(DeviceGroupBase)
    assert "name" in hints
    assert "description" in hints
    assert hints["name"] == str
    assert hints["description"] in (str | None, "Optional[str]")  # Python 3.10+ or older syntax

