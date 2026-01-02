"""Tests for Device Group API (Task 039)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from device_service.models.device_group import DeviceGroup
from device_service.models.device import Device, DeviceStatus
from school_service.core.security import hash_password
from shared.schemas.user import UserResponse


@pytest.fixture
async def test_school(test_db: AsyncSession) -> School:
    """Create a test school in the database."""
    school = School(
        name="Greenfield Academy",
        code="GFA-DEV-001",
        address="Nairobi, Kenya",
        phone="+254712345678",
        email="admin@greenfield.ac.ke",
        is_deleted=False,
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    return school


@pytest.fixture
async def test_user(test_db: AsyncSession, test_school: School) -> User:
    """Create a test user in the database."""
    user = User(
        school_id=test_school.id,
        email="admin@greenfield.ac.ke",
        hashed_password=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        role="school_admin",
        is_active=True,
        is_deleted=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_device_group(test_db: AsyncSession, test_school: School) -> DeviceGroup:
    """Create a test device group in the database."""
    device_group = DeviceGroup(
        school_id=test_school.id,
        name="Main Gate",
        description="Devices at the main gate entrance",
        is_deleted=False,
    )
    test_db.add(device_group)
    await test_db.commit()
    await test_db.refresh(device_group)
    return device_group


@pytest.fixture
async def authenticated_client(
    client: AsyncClient, test_user: User, test_db: AsyncSession
) -> AsyncClient:
    """
    Create an authenticated test client.
    
    Overrides get_current_user dependency to return the test user.
    """
    from device_service.main import app
    from device_service.api.dependencies import get_current_user

    async def override_get_current_user():
        """Override get_current_user to return test user."""
        return UserResponse.model_validate(test_user)

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield client

    # Clean up
    if get_current_user in app.dependency_overrides:
        app.dependency_overrides.pop(get_current_user)


# ============================================================================
# Create Device Group API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_group_success(authenticated_client: AsyncClient, test_school: School):
    """Test successful device group creation."""
    payload = {
        "name": "Library",
        "description": "Devices in the library",
    }
    
    response = await authenticated_client.post("/api/v1/device-groups", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["school_id"] == test_school.id
    assert data["device_count"] == 0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_group_without_auth(client: AsyncClient):
    """Test device group creation without authentication."""
    payload = {
        "name": "Test Group",
        "description": "Test description",
    }
    
    response = await client.post("/api/v1/device-groups", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_group_duplicate_name(
    authenticated_client: AsyncClient, test_device_group: DeviceGroup
):
    """Test device group creation with duplicate name."""
    payload = {
        "name": test_device_group.name,  # Same name
        "description": "Different description",
    }
    
    response = await authenticated_client.post("/api/v1/device-groups", json=payload)
    
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_group_invalid_name_min_length(authenticated_client: AsyncClient):
    """Test device group creation with name too short."""
    payload = {
        "name": "",  # Empty name
        "description": "Test description",
    }
    
    response = await authenticated_client.post("/api/v1/device-groups", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_group_invalid_name_max_length(authenticated_client: AsyncClient):
    """Test device group creation with name too long."""
    payload = {
        "name": "a" * 201,  # 201 characters (exceeds max of 200)
        "description": "Test description",
    }
    
    response = await authenticated_client.post("/api/v1/device-groups", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_group_without_description(authenticated_client: AsyncClient, test_school: School):
    """Test device group creation without description (optional field)."""
    payload = {
        "name": "Dormitories",
    }
    
    response = await authenticated_client.post("/api/v1/device-groups", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] is None


# ============================================================================
# List Device Groups API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_list_device_groups_success(
    authenticated_client: AsyncClient, test_device_group: DeviceGroup
):
    """Test listing device groups."""
    response = await authenticated_client.get("/api/v1/device-groups")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert len(data["items"]) >= 1
    assert data["total"] >= 1
    
    # Check that our test group is in the list
    group_ids = [item["id"] for item in data["items"]]
    assert test_device_group.id in group_ids


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_device_groups_without_auth(client: AsyncClient):
    """Test listing device groups without authentication."""
    response = await client.get("/api/v1/device-groups")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_device_groups_pagination(authenticated_client: AsyncClient, test_db: AsyncSession, test_school: School):
    """Test listing device groups with pagination."""
    # Create multiple groups
    for i in range(5):
        group = DeviceGroup(
            school_id=test_school.id,
            name=f"Group {i}",
            is_deleted=False,
        )
        test_db.add(group)
    await test_db.commit()
    
    # Test first page
    response = await authenticated_client.get("/api/v1/device-groups?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    
    # Test second page
    response = await authenticated_client.get("/api/v1/device-groups?page=2&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 2


# ============================================================================
# Get Device Group API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_group_success(
    authenticated_client: AsyncClient, test_device_group: DeviceGroup
):
    """Test getting a device group by ID."""
    response = await authenticated_client.get(f"/api/v1/device-groups/{test_device_group.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_device_group.id
    assert data["name"] == test_device_group.name
    assert data["description"] == test_device_group.description
    assert data["device_count"] == 0
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_group_not_found(authenticated_client: AsyncClient):
    """Test getting a non-existent device group."""
    response = await authenticated_client.get("/api/v1/device-groups/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_group_without_auth(client: AsyncClient):
    """Test getting a device group without authentication."""
    response = await client.get("/api/v1/device-groups/1")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_group_with_devices(
    authenticated_client: AsyncClient, test_db: AsyncSession, test_device_group: DeviceGroup, test_school: School
):
    """Test getting a device group with devices (device_count > 0)."""
    # Create devices in the group
    device1 = Device(
        school_id=test_school.id,
        name="Device 1",
        ip_address="192.168.1.100",
        port=4370,
        device_group_id=test_device_group.id,
        status=DeviceStatus.UNKNOWN,
        is_deleted=False,
    )
    device2 = Device(
        school_id=test_school.id,
        name="Device 2",
        ip_address="192.168.1.101",
        port=4370,
        device_group_id=test_device_group.id,
        status=DeviceStatus.UNKNOWN,
        is_deleted=False,
    )
    test_db.add_all([device1, device2])
    await test_db.commit()
    
    response = await authenticated_client.get(f"/api/v1/device-groups/{test_device_group.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["device_count"] == 2


# ============================================================================
# Update Device Group API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_group_success(
    authenticated_client: AsyncClient, test_device_group: DeviceGroup
):
    """Test updating a device group."""
    payload = {
        "name": "Updated Gate",
        "description": "Updated description",
    }
    
    response = await authenticated_client.patch(
        f"/api/v1/device-groups/{test_device_group.id}",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_group_partial(
    authenticated_client: AsyncClient, test_device_group: DeviceGroup
):
    """Test partial update of a device group (only name)."""
    original_description = test_device_group.description
    payload = {
        "name": "Updated Name Only",
    }
    
    response = await authenticated_client.patch(
        f"/api/v1/device-groups/{test_device_group.id}",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == original_description  # Unchanged


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_group_not_found(authenticated_client: AsyncClient):
    """Test updating a non-existent device group."""
    payload = {
        "name": "Updated Name",
    }
    
    response = await authenticated_client.patch(
        "/api/v1/device-groups/99999",
        json=payload
    )
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_group_duplicate_name(
    authenticated_client: AsyncClient, test_db: AsyncSession, test_school: School, test_device_group: DeviceGroup
):
    """Test updating a device group with duplicate name."""
    # Create another group
    other_group = DeviceGroup(
        school_id=test_school.id,
        name="Other Group",
        is_deleted=False,
    )
    test_db.add(other_group)
    await test_db.commit()
    
    # Try to update test_device_group to have the same name as other_group
    payload = {
        "name": other_group.name,
    }
    
    response = await authenticated_client.patch(
        f"/api/v1/device-groups/{test_device_group.id}",
        json=payload
    )
    
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_group_without_auth(client: AsyncClient):
    """Test updating a device group without authentication."""
    payload = {
        "name": "Updated Name",
    }
    
    response = await client.patch("/api/v1/device-groups/1", json=payload)
    assert response.status_code == 401


# ============================================================================
# Delete Device Group API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_device_group_success(
    authenticated_client: AsyncClient, test_db: AsyncSession, test_school: School
):
    """Test deleting a device group (soft delete)."""
    # Create a group to delete
    group = DeviceGroup(
        school_id=test_school.id,
        name="Group to Delete",
        is_deleted=False,
    )
    test_db.add(group)
    await test_db.commit()
    await test_db.refresh(group)
    
    response = await authenticated_client.delete(f"/api/v1/device-groups/{group.id}")
    
    assert response.status_code == 204
    
    # Verify it's soft-deleted (should not appear in list)
    list_response = await authenticated_client.get("/api/v1/device-groups")
    list_data = list_response.json()
    group_ids = [item["id"] for item in list_data["items"]]
    assert group.id not in group_ids


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_device_group_not_found(authenticated_client: AsyncClient):
    """Test deleting a non-existent device group."""
    response = await authenticated_client.delete("/api/v1/device-groups/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_device_group_without_auth(client: AsyncClient):
    """Test deleting a device group without authentication."""
    response = await client.delete("/api/v1/device-groups/1")
    assert response.status_code == 401

