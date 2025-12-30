"""Tests for Device Schemas (Task 028)."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from shared.schemas.device import (
    DeviceStatus,
    DeviceBase,
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    DeviceConnectionTest,
    DeviceConnectionTestResponse,
)


def test_device_status_enum():
    """Test that DeviceStatus enum has correct values."""
    assert DeviceStatus.ONLINE == "online"
    assert DeviceStatus.OFFLINE == "offline"
    assert DeviceStatus.UNKNOWN == "unknown"


def test_device_base_schema_valid_ipv4():
    """Test DeviceBase schema with valid IPv4 address."""
    device = DeviceBase(
        name="Test Device",
        ip_address="192.168.1.100",
        port=4370,
    )
    assert device.name == "Test Device"
    assert device.ip_address == "192.168.1.100"
    assert device.port == 4370


def test_device_base_schema_valid_ipv6():
    """Test DeviceBase schema with valid IPv6 address."""
    device = DeviceBase(
        name="Test Device",
        ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        port=4370,
    )
    assert device.ip_address == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"


def test_device_base_schema_invalid_ip():
    """Test DeviceBase schema with invalid IP address."""
    with pytest.raises(ValidationError) as exc_info:
        DeviceBase(
            name="Test Device",
            ip_address="invalid-ip",
            port=4370,
        )
    assert "Invalid IP address format" in str(exc_info.value)


def test_device_base_schema_port_default():
    """Test DeviceBase schema uses default port."""
    device = DeviceBase(
        name="Test Device",
        ip_address="192.168.1.100",
    )
    assert device.port == 4370


def test_device_base_schema_port_validation_min():
    """Test DeviceBase schema port validation (minimum)."""
    with pytest.raises(ValidationError):
        DeviceBase(
            name="Test Device",
            ip_address="192.168.1.100",
            port=0,
        )


def test_device_base_schema_port_validation_max():
    """Test DeviceBase schema port validation (maximum)."""
    with pytest.raises(ValidationError):
        DeviceBase(
            name="Test Device",
            ip_address="192.168.1.100",
            port=65536,
        )


def test_device_base_schema_name_validation_min():
    """Test DeviceBase schema name validation (minimum length)."""
    with pytest.raises(ValidationError):
        DeviceBase(
            name="",
            ip_address="192.168.1.100",
        )


def test_device_base_schema_name_validation_max():
    """Test DeviceBase schema name validation (maximum length)."""
    with pytest.raises(ValidationError):
        DeviceBase(
            name="a" * 201,  # 201 characters
            ip_address="192.168.1.100",
        )


def test_device_base_schema_optional_fields():
    """Test DeviceBase schema optional fields."""
    device = DeviceBase(
        name="Test Device",
        ip_address="192.168.1.100",
        serial_number="SN-001",
        location="Main Gate",
        description="Test device description",
    )
    assert device.serial_number == "SN-001"
    assert device.location == "Main Gate"
    assert device.description == "Test device description"


def test_device_create_schema():
    """Test DeviceCreate schema."""
    device = DeviceCreate(
        name="Test Device",
        ip_address="192.168.1.100",
        device_group_id=1,
    )
    assert device.device_group_id == 1


def test_device_update_schema_all_optional():
    """Test DeviceUpdate schema with all fields optional."""
    device = DeviceUpdate()
    assert device.name is None
    assert device.ip_address is None
    assert device.port is None


def test_device_update_schema_partial_update():
    """Test DeviceUpdate schema with partial update."""
    device = DeviceUpdate(
        name="Updated Name",
    )
    assert device.name == "Updated Name"
    assert device.ip_address is None


def test_device_update_schema_ip_validation():
    """Test DeviceUpdate schema IP address validation."""
    # Valid IP
    device = DeviceUpdate(ip_address="192.168.1.100")
    assert device.ip_address == "192.168.1.100"

    # Invalid IP
    with pytest.raises(ValidationError) as exc_info:
        DeviceUpdate(ip_address="invalid-ip")
    assert "Invalid IP address format" in str(exc_info.value)

    # None should be valid
    device = DeviceUpdate(ip_address=None)
    assert device.ip_address is None


def test_device_response_schema():
    """Test DeviceResponse schema."""
    device = DeviceResponse(
        id=1,
        school_id=1,
        name="Test Device",
        ip_address="192.168.1.100",
        port=4370,
        status=DeviceStatus.ONLINE,
        enrolled_users=0,
        created_at=datetime.utcnow(),
    )
    assert device.id == 1
    assert device.school_id == 1
    assert device.status == DeviceStatus.ONLINE
    assert device.enrolled_users == 0


def test_device_response_schema_optional_fields():
    """Test DeviceResponse schema optional fields."""
    device = DeviceResponse(
        id=1,
        school_id=1,
        name="Test Device",
        ip_address="192.168.1.100",
        port=4370,
        status=DeviceStatus.ONLINE,
        enrolled_users=0,
        created_at=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        max_users=1000,
        device_group_id=1,
    )
    assert device.last_seen is not None
    assert device.max_users == 1000
    assert device.device_group_id == 1


def test_device_list_response_schema():
    """Test DeviceListResponse schema."""
    devices = [
        DeviceResponse(
            id=1,
            school_id=1,
            name="Device 1",
            ip_address="192.168.1.100",
            port=4370,
            status=DeviceStatus.ONLINE,
            enrolled_users=0,
            created_at=datetime.utcnow(),
        ),
        DeviceResponse(
            id=2,
            school_id=1,
            name="Device 2",
            ip_address="192.168.1.101",
            port=4370,
            status=DeviceStatus.OFFLINE,
            enrolled_users=0,
            created_at=datetime.utcnow(),
        ),
    ]

    response = DeviceListResponse(
        items=devices,
        total=2,
        page=1,
        page_size=50,
        pages=1,
    )
    assert len(response.items) == 2
    assert response.total == 2
    assert response.page == 1
    assert response.pages == 1


def test_device_connection_test_schema_default_timeout():
    """Test DeviceConnectionTest schema default timeout."""
    test = DeviceConnectionTest()
    assert test.timeout == 5


def test_device_connection_test_schema_custom_timeout():
    """Test DeviceConnectionTest schema custom timeout."""
    test = DeviceConnectionTest(timeout=10)
    assert test.timeout == 10


def test_device_connection_test_schema_timeout_validation():
    """Test DeviceConnectionTest schema timeout validation."""
    # Minimum
    with pytest.raises(ValidationError):
        DeviceConnectionTest(timeout=0)

    # Maximum
    with pytest.raises(ValidationError):
        DeviceConnectionTest(timeout=31)


def test_device_connection_test_response_schema_success():
    """Test DeviceConnectionTestResponse schema for successful connection."""
    response = DeviceConnectionTestResponse(
        success=True,
        message="Connection successful",
        device_info={"model": "ZK-Teco F18", "firmware": "6.60.1.0"},
        response_time_ms=150,
    )
    assert response.success is True
    assert response.message == "Connection successful"
    assert response.device_info is not None
    assert response.response_time_ms == 150


def test_device_connection_test_response_schema_failure():
    """Test DeviceConnectionTestResponse schema for failed connection."""
    response = DeviceConnectionTestResponse(
        success=False,
        message="Connection timeout",
    )
    assert response.success is False
    assert response.message == "Connection timeout"
    assert response.device_info is None
    assert response.response_time_ms is None

