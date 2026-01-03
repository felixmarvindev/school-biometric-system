"""Tests for WebSocket device status updates (Task 042)."""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from device_service.models.device import Device, DeviceStatus
from school_service.core.security import hash_password, create_access_token
from shared.schemas.user import UserResponse
from device_service.services.device_status_broadcaster import DeviceStatusBroadcaster, broadcaster
from fastapi import WebSocket


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
        status=DeviceStatus.ONLINE,
        last_seen=datetime.utcnow(),
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
def mock_websocket():
    """Create a mock WebSocket for testing."""
    ws = AsyncMock(spec=WebSocket)
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_broadcaster_initialization():
    """Test that broadcaster initializes correctly."""
    broadcaster_instance = DeviceStatusBroadcaster()
    assert broadcaster_instance._connections == {}
    assert broadcaster_instance.get_connection_count() == 0


@pytest.mark.asyncio
async def test_broadcaster_connect(mock_websocket):
    """Test connecting a WebSocket."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    
    await broadcaster_instance.connect(mock_websocket, school_id)
    
    assert mock_websocket.accept.called
    assert school_id in broadcaster_instance._connections
    assert mock_websocket in broadcaster_instance._connections[school_id]
    assert broadcaster_instance.get_connection_count(school_id) == 1


@pytest.mark.asyncio
async def test_broadcaster_disconnect(mock_websocket):
    """Test disconnecting a WebSocket."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    
    await broadcaster_instance.connect(mock_websocket, school_id)
    assert broadcaster_instance.get_connection_count(school_id) == 1
    
    broadcaster_instance.disconnect(mock_websocket, school_id)
    
    assert broadcaster_instance.get_connection_count(school_id) == 0
    assert school_id not in broadcaster_instance._connections


@pytest.mark.asyncio
async def test_broadcaster_multiple_connections(mock_websocket):
    """Test multiple connections for same school."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    
    # Create multiple mock websockets
    ws1 = AsyncMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws2 = AsyncMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws3 = AsyncMock(spec=WebSocket)
    ws3.accept = AsyncMock()
    
    await broadcaster_instance.connect(ws1, school_id)
    await broadcaster_instance.connect(ws2, school_id)
    await broadcaster_instance.connect(ws3, school_id)
    
    assert broadcaster_instance.get_connection_count(school_id) == 3
    assert len(broadcaster_instance._connections[school_id]) == 3


@pytest.mark.asyncio
async def test_broadcaster_multiple_schools(mock_websocket):
    """Test connections for different schools."""
    broadcaster_instance = DeviceStatusBroadcaster()
    
    ws1 = AsyncMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws2 = AsyncMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    
    await broadcaster_instance.connect(ws1, school_id=1)
    await broadcaster_instance.connect(ws2, school_id=2)
    
    assert broadcaster_instance.get_connection_count(1) == 1
    assert broadcaster_instance.get_connection_count(2) == 1
    assert broadcaster_instance.get_connection_count() == 2


@pytest.mark.asyncio
async def test_broadcast_device_status_single_connection(mock_websocket):
    """Test broadcasting to a single connection."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    device_id = 1
    status = "online"
    last_seen = datetime.utcnow()
    
    await broadcaster_instance.connect(mock_websocket, school_id)
    await broadcaster_instance.broadcast_device_status(
        school_id=school_id,
        device_id=device_id,
        status=status,
        last_seen=last_seen,
    )
    
    # Verify message was sent
    assert mock_websocket.send_json.called
    call_args = mock_websocket.send_json.call_args[0][0]
    
    assert call_args["type"] == "device_status_update"
    assert call_args["device_id"] == device_id
    assert call_args["status"] == status
    assert call_args["last_seen"] == last_seen.isoformat()
    assert "timestamp" in call_args


@pytest.mark.asyncio
async def test_broadcast_device_status_multiple_connections():
    """Test broadcasting to multiple connections."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    device_id = 1
    status = "online"
    
    # Create multiple mock websockets
    ws1 = AsyncMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    ws2 = AsyncMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    ws3 = AsyncMock(spec=WebSocket)
    ws3.accept = AsyncMock()
    ws3.send_json = AsyncMock()
    
    await broadcaster_instance.connect(ws1, school_id)
    await broadcaster_instance.connect(ws2, school_id)
    await broadcaster_instance.connect(ws3, school_id)
    
    await broadcaster_instance.broadcast_device_status(
        school_id=school_id,
        device_id=device_id,
        status=status,
    )
    
    # Verify all connections received the message
    assert ws1.send_json.called
    assert ws2.send_json.called
    assert ws3.send_json.called


@pytest.mark.asyncio
async def test_broadcast_device_status_no_connections():
    """Test broadcasting when no connections exist."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 999  # No connections for this school
    
    # Should not raise an error
    await broadcaster_instance.broadcast_device_status(
        school_id=school_id,
        device_id=1,
        status="online",
    )


@pytest.mark.asyncio
async def test_broadcast_device_status_offline_status():
    """Test broadcasting offline status with null last_seen."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    
    ws = AsyncMock(spec=WebSocket)
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    
    await broadcaster_instance.connect(ws, school_id)
    
    await broadcaster_instance.broadcast_device_status(
        school_id=school_id,
        device_id=1,
        status="offline",
        last_seen=None,
    )
    
    assert ws.send_json.called
    call_args = ws.send_json.call_args[0][0]
    assert call_args["status"] == "offline"
    assert call_args["last_seen"] is None


@pytest.mark.asyncio
async def test_broadcast_handles_disconnected_client():
    """Test that disconnected clients are removed when sending fails."""
    broadcaster_instance = DeviceStatusBroadcaster()
    school_id = 1
    
    # Create websockets
    ws1 = AsyncMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()  # Works fine
    
    ws2 = AsyncMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock(side_effect=Exception("Connection closed"))  # Fails
    
    await broadcaster_instance.connect(ws1, school_id)
    await broadcaster_instance.connect(ws2, school_id)
    
    assert broadcaster_instance.get_connection_count(school_id) == 2
    
    # Broadcast should remove the disconnected client
    await broadcaster_instance.broadcast_device_status(
        school_id=school_id,
        device_id=1,
        status="online",
    )
    
    # Only ws1 should still be connected
    assert broadcaster_instance.get_connection_count(school_id) == 1
    assert ws1 in broadcaster_instance._connections[school_id]
    assert ws2 not in broadcaster_instance._connections[school_id]


@pytest.mark.asyncio
async def test_broadcast_school_isolation():
    """Test that broadcasts only go to the correct school."""
    broadcaster_instance = DeviceStatusBroadcaster()
    
    ws1 = AsyncMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = AsyncMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await broadcaster_instance.connect(ws1, school_id=1)
    await broadcaster_instance.connect(ws2, school_id=2)
    
    # Broadcast to school 1
    await broadcaster_instance.broadcast_device_status(
        school_id=1,
        device_id=1,
        status="online",
    )
    
    # Only ws1 should receive the message
    assert ws1.send_json.called
    assert not ws2.send_json.called


@pytest.mark.asyncio
async def test_get_connection_count():
    """Test getting connection counts."""
    broadcaster_instance = DeviceStatusBroadcaster()
    
    ws1 = AsyncMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws2 = AsyncMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws3 = AsyncMock(spec=WebSocket)
    ws3.accept = AsyncMock()
    
    await broadcaster_instance.connect(ws1, school_id=1)
    await broadcaster_instance.connect(ws2, school_id=1)
    await broadcaster_instance.connect(ws3, school_id=2)
    
    # Test per-school count
    assert broadcaster_instance.get_connection_count(1) == 2
    assert broadcaster_instance.get_connection_count(2) == 1
    
    # Test total count
    assert broadcaster_instance.get_connection_count() == 3


@pytest.mark.asyncio
async def test_websocket_endpoint_authentication_success(test_db: AsyncSession, test_user: User, auth_token: str):
    """Test WebSocket endpoint with valid authentication."""
    from device_service.api.dependencies import get_current_user_ws
    from contextlib import asynccontextmanager
    from device_service.core.database import AsyncSessionLocal
    
    # Ensure user is committed to database
    await test_db.commit()
    await test_db.refresh(test_user)
    
    # Verify user exists in database
    from school_service.services.user_service import UserService
    user_service = UserService(test_db)
    db_user = await user_service.get_user_by_id(test_user.id)
    assert db_user is not None, "Test user should exist in database"
    
    # Patch AsyncSessionLocal to use test_db
    # Note: AsyncSessionLocal is imported inside get_current_user_ws, so we patch it at module level
    @asynccontextmanager
    async def mock_session_context():
        yield test_db
    
    class MockSessionLocal:
        def __call__(self):
            return mock_session_context()
    
    # Patch where it's imported (in the dependencies module)
    with patch('device_service.core.database.AsyncSessionLocal', MockSessionLocal()):
        user = await get_current_user_ws(auth_token)
        assert user is not None
        assert user.id == test_user.id
        assert user.school_id == test_user.school_id


@pytest.mark.asyncio
async def test_websocket_endpoint_authentication_failure():
    """Test WebSocket endpoint with invalid authentication."""
    from device_service.api.dependencies import get_current_user_ws
    
    # Invalid token
    user = await get_current_user_ws("invalid_token")
    assert user is None


@pytest.mark.asyncio
async def test_broadcaster_integration_with_health_check(
    test_db: AsyncSession,
    test_school: School,
    test_device: Device
):
    """Test that health check service broadcasts updates."""
    from device_service.services.device_health_check import DeviceHealthCheckService
    from unittest.mock import AsyncMock, patch
    
    # Mock connection service to return True (online)
    health_check = DeviceHealthCheckService()
    health_check.connection_service.test_connection = AsyncMock(return_value=True)
    
    # Track broadcasts
    broadcast_calls = []
    
    async def mock_broadcast(school_id, device_id, status, last_seen=None):
        broadcast_calls.append({
            "school_id": school_id,
            "device_id": device_id,
            "status": status,
            "last_seen": last_seen,
        })
    
    # Patch broadcaster
    with patch.object(broadcaster, 'broadcast_device_status', mock_broadcast):
        with patch('device_service.services.device_health_check.settings') as mock_settings:
            mock_settings.SIMULATION_MODE = False
            mock_settings.DEFAULT_DEVICE_TIMEOUT = 5
            
            # Check device (should update status and broadcast)
            await health_check.check_device(test_device, test_db)
            
            # Verify broadcast was called
            assert len(broadcast_calls) == 1
            assert broadcast_calls[0]["device_id"] == test_device.id
            assert broadcast_calls[0]["school_id"] == test_device.school_id
            assert broadcast_calls[0]["status"] == "online"

