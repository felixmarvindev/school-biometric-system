"""Tests for Device API (Tasks 029-034)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from device_service.models.device import Device, DeviceStatus
from school_service.core.security import hash_password, create_access_token
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
async def test_device(test_db: AsyncSession, test_school: School) -> Device:
    """Create a test device in the database."""
    device = Device(
        school_id=test_school.id,
        name="Main Gate Scanner",
        ip_address="192.168.1.100",
        port=4370,
        serial_number="DEV-001",
        location="Main Gate",
        description="Primary entry point scanner",
        status=DeviceStatus.UNKNOWN,
        is_deleted=False,
    )
    test_db.add(device)
    await test_db.commit()
    await test_db.refresh(device)
    return device


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    return create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "first_name": test_user.first_name,
            "last_name": test_user.last_name,
            "school_id": test_user.school_id,
            "role": test_user.role,
        }
    )


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
# Task 029: Create Device API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_success(authenticated_client: AsyncClient, test_school: School):
    """Test successful device creation."""
    payload = {
        "name": "Library Scanner",
        "ip_address": "192.168.1.101",
        "port": 4370,
        "location": "Library",
        "description": "Library entrance scanner",
    }
    
    response = await authenticated_client.post("/api/v1/devices", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["ip_address"] == payload["ip_address"]
    assert data["port"] == payload["port"]
    assert data["school_id"] == test_school.id
    assert data["status"] == "unknown"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_without_auth(client: AsyncClient):
    """Test device creation without authentication."""
    payload = {
        "name": "Test Device",
        "ip_address": "192.168.1.102",
        "port": 4370,
    }
    
    response = await client.post("/api/v1/devices", json=payload)
    
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_duplicate_ip_port(authenticated_client: AsyncClient, test_device: Device):
    """Test device creation with duplicate IP/port in same school."""
    payload = {
        "name": "Duplicate Device",
        "ip_address": test_device.ip_address,  # Same IP
        "port": test_device.port,  # Same port
    }
    
    response = await authenticated_client.post("/api/v1/devices", json=payload)
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_duplicate_serial(authenticated_client: AsyncClient, test_device: Device):
    """Test device creation with duplicate serial number."""
    payload = {
        "name": "Duplicate Serial Device",
        "ip_address": "192.168.1.103",
        "port": 4370,
        "serial_number": test_device.serial_number,  # Same serial number
    }
    
    response = await authenticated_client.post("/api/v1/devices", json=payload)
    
    assert response.status_code == 409
    assert "serial number" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_device_validation_error(authenticated_client: AsyncClient):
    """Test device creation with validation errors."""
    payload = {
        "name": "",  # Empty name (should fail)
        "ip_address": "invalid-ip",  # Invalid IP
        "port": 65536,  # Invalid port (too high)
    }
    
    response = await authenticated_client.post("/api/v1/devices", json=payload)
    
    assert response.status_code == 422


# ============================================================================
# Task 030: List Devices API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_list_devices_success(authenticated_client: AsyncClient, test_device: Device):
    """Test successful device listing."""
    response = await authenticated_client.get("/api/v1/devices")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert len(data["items"]) > 0
    assert data["total"] > 0


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_devices_pagination(authenticated_client: AsyncClient, test_school: School, test_db: AsyncSession):
    """Test device listing with pagination."""
    # Create multiple devices
    for i in range(5):
        device = Device(
            school_id=test_school.id,
            name=f"Device {i}",
            ip_address=f"192.168.1.{200+i}",
            port=4370 + i,
            is_deleted=False,
        )
        test_db.add(device)
    await test_db.commit()
    
    # Test pagination
    response = await authenticated_client.get("/api/v1/devices?page=1&page_size=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_devices_search(authenticated_client: AsyncClient, test_device: Device):
    """Test device listing with search."""
    response = await authenticated_client.get(f"/api/v1/devices?search={test_device.name}")
    
    assert response.status_code == 200
    data = response.json()
    assert any(d["name"] == test_device.name for d in data["items"])


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_devices_filter_by_status(authenticated_client: AsyncClient, test_device: Device, test_db: AsyncSession):
    """Test device listing filtered by status."""
    # Update device status
    test_device.status = DeviceStatus.ONLINE
    await test_db.commit()
    
    response = await authenticated_client.get("/api/v1/devices?status=online")
    
    assert response.status_code == 200
    data = response.json()
    assert all(d["status"] == "online" for d in data["items"])


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_devices_without_auth(client: AsyncClient):
    """Test device listing without authentication."""
    response = await client.get("/api/v1/devices")
    
    assert response.status_code == 401


# ============================================================================
# Task 031: Get Device API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_success(authenticated_client: AsyncClient, test_device: Device):
    """Test successful device retrieval."""
    response = await authenticated_client.get(f"/api/v1/devices/{test_device.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_device.id
    assert data["name"] == test_device.name
    assert data["ip_address"] == test_device.ip_address


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_not_found(authenticated_client: AsyncClient):
    """Test device retrieval with non-existent ID."""
    response = await authenticated_client.get("/api/v1/devices/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_different_school(authenticated_client: AsyncClient, test_db: AsyncSession):
    """Test device retrieval from different school."""
    # Create another school and device
    other_school = School(
        name="Other School",
        code="OTHER-001",
        is_deleted=False,
    )
    test_db.add(other_school)
    await test_db.commit()
    await test_db.refresh(other_school)
    
    other_device = Device(
        school_id=other_school.id,
        name="Other Device",
        ip_address="192.168.1.200",
        port=4370,
        is_deleted=False,
    )
    test_db.add(other_device)
    await test_db.commit()
    await test_db.refresh(other_device)
    
    # Try to access device from different school
    response = await authenticated_client.get(f"/api/v1/devices/{other_device.id}")
    
    assert response.status_code == 404  # Should not find it (authorization)


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_device_without_auth(client: AsyncClient):
    """Test device retrieval without authentication."""
    response = await client.get("/api/v1/devices/1")
    
    assert response.status_code == 401


# ============================================================================
# Task 032: Update Device API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_success(authenticated_client: AsyncClient, test_device: Device):
    """Test successful device update."""
    payload = {
        "name": "Updated Device Name",
        "location": "Updated Location",
    }
    
    response = await authenticated_client.patch(
        f"/api/v1/devices/{test_device.id}",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["location"] == payload["location"]


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_partial(authenticated_client: AsyncClient, test_device: Device):
    """Test partial device update (only name)."""
    original_location = test_device.location
    payload = {
        "name": "Partially Updated",
    }
    
    response = await authenticated_client.patch(
        f"/api/v1/devices/{test_device.id}",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["location"] == original_location  # Should remain unchanged


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_duplicate_ip_port(authenticated_client: AsyncClient, test_device: Device, test_db: AsyncSession):
    """Test device update with duplicate IP/port."""
    # Create another device
    other_device = Device(
        school_id=test_device.school_id,
        name="Other Device",
        ip_address="192.168.1.105",
        port=4371,
        is_deleted=False,
    )
    test_db.add(other_device)
    await test_db.commit()
    await test_db.refresh(other_device)
    
    # Try to update device to use same IP/port as other device
    payload = {
        "ip_address": other_device.ip_address,
        "port": other_device.port,
    }
    
    response = await authenticated_client.patch(
        f"/api/v1/devices/{test_device.id}",
        json=payload
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_not_found(authenticated_client: AsyncClient):
    """Test device update with non-existent ID."""
    payload = {"name": "Updated"}
    
    response = await authenticated_client.patch(
        "/api/v1/devices/99999",
        json=payload
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_device_without_auth(client: AsyncClient):
    """Test device update without authentication."""
    payload = {"name": "Updated"}
    
    response = await client.patch("/api/v1/devices/1", json=payload)
    
    assert response.status_code == 401


# ============================================================================
# Task 033: Delete Device API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_device_success(authenticated_client: AsyncClient, test_device: Device):
    """Test successful device deletion."""
    response = await authenticated_client.delete(f"/api/v1/devices/{test_device.id}")
    
    assert response.status_code == 204
    
    # Verify device is soft-deleted (not returned in list)
    list_response = await authenticated_client.get("/api/v1/devices")
    assert list_response.status_code == 200
    device_ids = [d["id"] for d in list_response.json()["items"]]
    assert test_device.id not in device_ids


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_device_not_found(authenticated_client: AsyncClient):
    """Test device deletion with non-existent ID."""
    response = await authenticated_client.delete("/api/v1/devices/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_device_without_auth(client: AsyncClient):
    """Test device deletion without authentication."""
    response = await client.delete("/api/v1/devices/1")
    
    assert response.status_code == 401


# ============================================================================
# Task 034: Connection Test API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_connection_test_success(authenticated_client: AsyncClient, test_device: Device):
    """Test device connection test (may fail if device not reachable, but endpoint should work)."""
    payload = {
        "timeout": 2,
    }
    
    response = await authenticated_client.post(
        f"/api/v1/devices/{test_device.id}/test",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data
    # Connection may succeed or fail depending on device availability
    assert data["success"] in [True, False]


@pytest.mark.asyncio
@pytest.mark.api
async def test_connection_test_not_found(authenticated_client: AsyncClient):
    """Test connection test with non-existent device."""
    payload = {"timeout": 2}
    
    response = await authenticated_client.post(
        "/api/v1/devices/99999/test",
        json=payload
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
async def test_connection_test_default_timeout(authenticated_client: AsyncClient, test_device: Device):
    """Test connection test with default timeout."""
    response = await authenticated_client.post(
        f"/api/v1/devices/{test_device.id}/test",
        json={}  # Empty payload should use defaults
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_connection_test_without_auth(client: AsyncClient):
    """Test connection test without authentication."""
    response = await client.post("/api/v1/devices/1/test", json={})
    
    assert response.status_code == 401

