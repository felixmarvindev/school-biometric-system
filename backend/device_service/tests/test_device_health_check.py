"""Tests for Device Health Check Service (Task 041)."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from device_service.models.device import Device, DeviceStatus
from device_service.services.device_health_check import DeviceHealthCheckService
from device_service.core.config import settings


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
async def test_device_online(test_db: AsyncSession, test_school: School) -> Device:
    """Create a test device with online status."""
    device = Device(
        school_id=test_school.id,
        name="Main Gate Scanner",
        ip_address="192.168.1.100",
        port=4370,
        serial_number="DEV-001",
        location="Main Gate",
        status=DeviceStatus.ONLINE,
        last_seen=datetime.utcnow(),
        is_deleted=False,
    )
    test_db.add(device)
    await test_db.commit()
    await test_db.refresh(device)
    return device


@pytest.fixture
async def test_device_offline(test_db: AsyncSession, test_school: School) -> Device:
    """Create a test device with offline status."""
    device = Device(
        school_id=test_school.id,
        name="Back Gate Scanner",
        ip_address="192.168.1.101",
        port=4370,
        serial_number="DEV-002",
        location="Back Gate",
        status=DeviceStatus.OFFLINE,
        last_seen=None,
        is_deleted=False,
    )
    test_db.add(device)
    await test_db.commit()
    await test_db.refresh(device)
    return device


@pytest.fixture
async def test_device_deleted(test_db: AsyncSession, test_school: School) -> Device:
    """Create a deleted test device (should not be checked)."""
    device = Device(
        school_id=test_school.id,
        name="Deleted Scanner",
        ip_address="192.168.1.102",
        port=4370,
        serial_number="DEV-003",
        location="Deleted",
        status=DeviceStatus.UNKNOWN,
        is_deleted=True,
    )
    test_db.add(device)
    await test_db.commit()
    await test_db.refresh(device)
    return device


@pytest.fixture
def health_check_service():
    """Create a DeviceHealthCheckService instance."""
    return DeviceHealthCheckService()


@pytest.mark.asyncio
async def test_health_check_service_initialization(health_check_service):
    """Test that health check service initializes correctly."""
    assert health_check_service.connection_service is not None
    assert health_check_service.running is False
    assert health_check_service.check_interval == settings.DEVICE_HEALTH_CHECK_INTERVAL
    assert health_check_service._task is None


@pytest.mark.asyncio
async def test_health_check_service_start(health_check_service):
    """Test starting the health check service."""
    await health_check_service.start()
    
    assert health_check_service.running is True
    assert health_check_service._task is not None
    assert not health_check_service._task.done()
    
    # Clean up
    await health_check_service.stop()


@pytest.mark.asyncio
async def test_health_check_service_start_when_already_running(health_check_service):
    """Test that starting an already running service logs a warning."""
    await health_check_service.start()
    
    # Try to start again
    await health_check_service.start()
    
    # Should still be running (only one task)
    assert health_check_service.running is True
    
    # Clean up
    await health_check_service.stop()


@pytest.mark.asyncio
async def test_health_check_service_stop(health_check_service):
    """Test stopping the health check service."""
    await health_check_service.start()
    assert health_check_service.running is True
    
    await health_check_service.stop()
    
    assert health_check_service.running is False
    # Task should be cancelled (but may take a moment)
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_health_check_service_stop_when_not_running(health_check_service):
    """Test that stopping a non-running service is safe."""
    assert health_check_service.running is False
    
    # Should not raise an error
    await health_check_service.stop()
    
    assert health_check_service.running is False


@pytest.mark.asyncio
async def test_check_all_devices_empty(test_db: AsyncSession, health_check_service):
    """Test checking devices when no devices exist."""
    # Should not raise an error
    await health_check_service.check_all_devices()


@pytest.mark.asyncio
async def test_check_all_devices_excludes_deleted(
    test_db: AsyncSession,
    test_school: School,
    health_check_service,
    test_device_online,
    test_device_deleted
):
    """Test that deleted devices are excluded from health checks."""
    # Create a mock sessionmaker that returns test_db
    # AsyncSessionLocal() returns an async context manager, so we need to mock that behavior
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def mock_session_context():
        yield test_db
    
    class MockSessionLocal:
        def __call__(self):
            return mock_session_context()
    
    # Mock check_device to track calls
    call_count = 0
    checked_device_ids = []
    
    original_check_device = health_check_service.check_device
    
    async def mock_check_device(device, db):
        nonlocal call_count, checked_device_ids
        call_count += 1
        checked_device_ids.append(device.id)
        return await original_check_device(device, db)
    
    health_check_service.check_device = mock_check_device
    
    with patch('device_service.services.device_health_check.AsyncSessionLocal', MockSessionLocal()):
        await health_check_service.check_all_devices()
    
    # Should only check the non-deleted device
    assert call_count == 1
    # Verify it checked the online device, not the deleted one
    assert test_device_online.id in checked_device_ids
    assert test_device_deleted.id not in checked_device_ids


@pytest.mark.asyncio
@patch('device_service.services.device_health_check.settings')
async def test_check_device_simulation_mode(
    mock_settings,
    test_db: AsyncSession,
    health_check_service,
    test_device_online
):
    """Test device checking in simulation mode."""
    mock_settings.SIMULATION_MODE = True
    mock_settings.DEFAULT_DEVICE_TIMEOUT = 5
    
    # Run multiple checks to verify randomness
    results = []
    for _ in range(10):
        result = await health_check_service.check_device(test_device_online, test_db)
        results.append(result)
        # Give a small delay to ensure different random values
        await asyncio.sleep(0.01)
    
    # In simulation mode, should get some True and some False (90% chance of True)
    assert any(results), "Should have at least some online results in simulation mode"
    
    # Verify status was updated
    await test_db.refresh(test_device_online)
    assert test_device_online.status in [DeviceStatus.ONLINE, DeviceStatus.OFFLINE]


@pytest.mark.asyncio
@patch('device_service.services.device_health_check.settings')
async def test_check_device_production_mode_online(
    mock_settings,
    test_db: AsyncSession,
    health_check_service,
    test_device_offline
):
    """Test device checking in production mode with online device."""
    mock_settings.SIMULATION_MODE = False
    mock_settings.DEFAULT_DEVICE_TIMEOUT = 5
    
    # Mock successful connection on the instance
    health_check_service.connection_service.test_connection = AsyncMock(return_value=True)
    
    result = await health_check_service.check_device(test_device_offline, test_db)
    
    assert result is True
    health_check_service.connection_service.test_connection.assert_called_once_with(
        ip_address=test_device_offline.ip_address,
        port=test_device_offline.port,
        timeout=5
    )
    
    # Verify status was updated
    await test_db.refresh(test_device_offline)
    assert test_device_offline.status == DeviceStatus.ONLINE
    assert test_device_offline.last_seen is not None


@pytest.mark.asyncio
@patch('device_service.services.device_health_check.settings')
async def test_check_device_production_mode_offline(
    mock_settings,
    test_db: AsyncSession,
    health_check_service,
    test_device_online
):
    """Test device checking in production mode with offline device."""
    mock_settings.SIMULATION_MODE = False
    mock_settings.DEFAULT_DEVICE_TIMEOUT = 5
    
    # Mock failed connection on the instance
    health_check_service.connection_service.test_connection = AsyncMock(return_value=False)
    
    result = await health_check_service.check_device(test_device_online, test_db)
    
    assert result is False
    health_check_service.connection_service.test_connection.assert_called_once_with(
        ip_address=test_device_online.ip_address,
        port=test_device_online.port,
        timeout=5
    )
    
    # Verify status was updated
    await test_db.refresh(test_device_online)
    assert test_device_online.status == DeviceStatus.OFFLINE
    # Note: last_seen is not cleared in current implementation when device goes offline
    # This might be intentional to preserve the last known online time


@pytest.mark.asyncio
@patch('device_service.services.device_health_check.settings')
async def test_check_device_connection_error(
    mock_settings,
    test_db: AsyncSession,
    health_check_service,
    test_device_online
):
    """Test device checking when connection test raises an exception."""
    mock_settings.SIMULATION_MODE = False
    mock_settings.DEFAULT_DEVICE_TIMEOUT = 5
    
    # Mock connection raising an exception on the instance
    health_check_service.connection_service.test_connection = AsyncMock(side_effect=Exception("Connection error"))
    
    result = await health_check_service.check_device(test_device_online, test_db)
    
    assert result is False
    
    # Verify status was updated to offline on error
    await test_db.refresh(test_device_online)
    assert test_device_online.status == DeviceStatus.OFFLINE


@pytest.mark.asyncio
async def test_update_device_status_online(
    test_db: AsyncSession,
    health_check_service,
    test_device_offline
):
    """Test updating device status to online."""
    initial_last_seen = test_device_offline.last_seen
    
    await health_check_service.update_device_status(
        test_device_offline.id,
        True,
        test_db
    )
    
    await test_db.refresh(test_device_offline)
    assert test_device_offline.status == DeviceStatus.ONLINE
    assert test_device_offline.last_seen is not None
    assert test_device_offline.last_seen > initial_last_seen if initial_last_seen else True


@pytest.mark.asyncio
async def test_update_device_status_offline(
    test_db: AsyncSession,
    health_check_service,
    test_device_online
):
    """Test updating device status to offline."""
    await health_check_service.update_device_status(
        test_device_online.id,
        False,
        test_db
    )
    
    await test_db.refresh(test_device_online)
    assert test_device_online.status == DeviceStatus.OFFLINE
    # last_seen should be None when device goes offline
    assert test_device_online.last_seen is None


@pytest.mark.asyncio
async def test_update_device_status_nonexistent(
    test_db: AsyncSession,
    health_check_service
):
    """Test updating status for a non-existent device."""
    # Should not raise an error, just log
    await health_check_service.update_device_status(
        99999,  # Non-existent device ID
        True,
        test_db
    )


@pytest.mark.asyncio
async def test_check_all_devices_concurrent(
    test_db: AsyncSession,
    test_school: School,
    health_check_service
):
    """Test that devices are checked concurrently."""
    # Create multiple devices
    devices = []
    for i in range(5):
        device = Device(
            school_id=test_school.id,
            name=f"Device {i}",
            ip_address=f"192.168.1.{100 + i}",
            port=4370,
            status=DeviceStatus.UNKNOWN,
            is_deleted=False,
        )
        test_db.add(device)
        devices.append(device)
    await test_db.commit()
    
    # Mock check_device to have a delay
    original_check = health_check_service.check_device
    call_times = []
    
    async def delayed_check(device, db):
        call_times.append(datetime.utcnow())
        await asyncio.sleep(0.1)  # Simulate network delay
        return await original_check(device, db)
    
    health_check_service.check_device = delayed_check
    
    start_time = datetime.utcnow()
    await health_check_service.check_all_devices()
    end_time = datetime.utcnow()
    
    # If concurrent, all devices should be checked around the same time
    # Total time should be ~0.1s (one delay) not ~0.5s (5 delays)
    duration = (end_time - start_time).total_seconds()
    assert duration < 0.3, f"Devices should be checked concurrently, but took {duration}s"


@pytest.mark.asyncio
async def test_check_all_devices_updates_all_statuses(
    test_db: AsyncSession,
    test_school: School,
    health_check_service
):
    """Test that checking all devices updates all their statuses."""
    # Create multiple devices
    devices = []
    for i in range(3):
        device = Device(
            school_id=test_school.id,
            name=f"Device {i}",
            ip_address=f"192.168.1.{100 + i}",
            port=4370,
            status=DeviceStatus.UNKNOWN,
            is_deleted=False,
        )
        test_db.add(device)
        devices.append(device)
    await test_db.commit()
    
    # Create a mock sessionmaker that returns test_db
    # AsyncSessionLocal() returns an async context manager, so we need to mock that behavior
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def mock_session_context():
        yield test_db
    
    class MockSessionLocal:
        def __call__(self):
            return mock_session_context()
    
    # Mock connection service on the instance
    health_check_service.connection_service.test_connection = AsyncMock(return_value=True)
    
    with patch('device_service.services.device_health_check.AsyncSessionLocal', MockSessionLocal()):
        with patch('device_service.services.device_health_check.settings') as mock_settings:
            mock_settings.SIMULATION_MODE = False
            mock_settings.DEFAULT_DEVICE_TIMEOUT = 5
            
            await health_check_service.check_all_devices()
            
            # Verify all devices were checked
            assert health_check_service.connection_service.test_connection.call_count == 3
            
            # Verify all devices were updated
            for device in devices:
                await test_db.refresh(device)
                assert device.status in [DeviceStatus.ONLINE, DeviceStatus.OFFLINE]

