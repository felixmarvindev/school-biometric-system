# ZKTeco Device Integration

This module provides async wrappers for communicating with ZKTeco biometric devices using the `pyzk` library.

## Installation

The `pyzk` library is included in `requirements.txt`:

```bash
pip install pyzk==0.9.0
```

## Usage

### Basic Connection

```python
from device_service.zk.base import ZKDeviceConnection

# Using async context manager
async with ZKDeviceConnection("192.168.1.100", 4370) as device:
    if device.is_connected:
        # Get device information
        serial = await device.get_serial_number()
        name = await device.get_device_name()
        version = await device.get_firmware_version()
        capacity = await device.get_free_sizes()
```

### Using DeviceConnectionService

```python
from device_service.services.device_connection import DeviceConnectionService
from device_service.models.device import Device

connection_service = DeviceConnectionService(db)

# Get connection for a device
device_model = await get_device(device_id)
conn = await connection_service.get_connection(device_model)

if conn:
    # Use connection
    serial = await conn.get_serial_number()
    # Connection is automatically cached and reused
```

### Testing Connection

```python
from device_service.services.device_connection import DeviceConnectionService

connection_service = DeviceConnectionService()

result = await connection_service.test_connection(
    ip_address="192.168.1.100",
    port=4370,
    password=None,  # Optional
    timeout=5,
)

if result["success"]:
    print(f"Connected! Response time: {result['response_time_ms']}ms")
    if result.get("device_info"):
        print(f"Serial: {result['device_info'].get('serial_number')}")
else:
    print(f"Connection failed: {result['message']}")
```

## Available Methods

### ZKDeviceConnection

- `connect()` - Establish connection (async)
- `disconnect()` - Close connection (async)
- `is_connected` - Check connection status (property)
- `get_serial_number()` - Get device serial number
- `get_device_name()` - Get device model/name
- `get_firmware_version()` - Get firmware version
- `get_time()` - Get device current time
- `get_free_sizes()` - Get device capacity (users, fingerprints, etc.)
- `test_connection()` - Test if connection is still active

## Configuration

Device connection settings can be configured in `device_service/core/config.py`:

- `DEFAULT_DEVICE_TIMEOUT` - Connection timeout (default: 5 seconds)
- `DEVICE_DEFAULT_PORT` - Default ZKTeco port (default: 4370)
- `DEVICE_CONNECTION_RETRY_ATTEMPTS` - Retry attempts (default: 3)
- `DEVICE_CONNECTION_RETRY_DELAY` - Retry delay in seconds (default: 1.0)
- `DEVICE_CONNECTION_POOL_SIZE` - Max concurrent connections (default: 10)

## Error Handling

The library handles various error scenarios:

- **Connection timeout** - Device is offline or unreachable
- **Connection refused** - Port is incorrect or device not listening
- **Network errors** - IP address incorrect or network issues
- **Protocol errors** - Device is not ZKTeco-compatible

All errors are logged and returned with user-friendly messages.

## Notes

- All operations are async and non-blocking
- Connections are automatically cached and reused
- The library wraps the synchronous `pyzk` library using `asyncio.to_thread`
- Connection pooling is handled by `DeviceConnectionService`
