# Task 041: Device Health Check Service

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 3: Device Monitoring

## Description

Create a background service that periodically checks device connectivity and updates device status and last_seen timestamps.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Health check service exists as background task
2. [x] Service checks all devices periodically (configurable interval)
3. [x] Updates device status (online/offline)
4. [x] Updates last_seen timestamp
5. [x] Handles connection timeouts gracefully
6. [x] Logs health check results
7. [x] Can be started/stopped
8. [x] Configurable check interval (default: 5 minutes)
9. [x] Respects simulation mode

## Technical Details

### Files to Create/Modify

```
backend/device_service/services/device_health_check.py
backend/device_service/services/device_connection.py
backend/device_service/core/config.py (add health check config)
```

### Key Code Patterns

```python
# services/device_health_check.py
import asyncio
import logging
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from device_service.models.device import Device, DeviceStatus
from device_service.services.device_connection import DeviceConnectionService
from device_service.core.config import settings

logger = logging.getLogger(__name__)

class DeviceHealthCheckService:
    """Background service for checking device connectivity."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.connection_service = DeviceConnectionService()
        self.running = False
        self.check_interval = settings.DEVICE_HEALTH_CHECK_INTERVAL  # seconds
        
    async def start(self):
        """Start the health check service."""
        if self.running:
            logger.warning("Health check service already running")
            return
        
        self.running = True
        logger.info(f"Starting device health check service (interval: {self.check_interval}s)")
        
        while self.running:
            try:
                await self.check_all_devices()
            except Exception as e:
                logger.error(f"Error in health check cycle: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the health check service."""
        self.running = False
        logger.info("Stopping device health check service")
    
    async def check_all_devices(self):
        """Check connectivity for all active devices."""
        from device_service.repositories.device_repository import DeviceRepository
        
        repo = DeviceRepository(self.db)
        devices = await repo.get_all_active_devices()
        
        logger.info(f"Checking {len(devices)} devices")
        
        # Check devices concurrently
        tasks = [self.check_device(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log summary
        online_count = sum(1 for r in results if r is True)
        offline_count = sum(1 for r in results if r is False)
        error_count = sum(1 for r in results if isinstance(r, Exception))
        
        logger.info(f"Health check complete: {online_count} online, {offline_count} offline, {error_count} errors")
    
    async def check_device(self, device: Device) -> bool:
        """Check connectivity for a single device."""
        try:
            # Skip simulation mode devices (handled separately)
            if settings.SIMULATION_MODE:
                # In simulation mode, simulate random online/offline
                import random
                is_online = random.random() > 0.1  # 90% online rate
                await self.update_device_status(device.id, is_online)
                return is_online
            
            # Test TCP connection
            is_online = await self.connection_service.test_connection(
                ip_address=device.ip_address,
                port=device.port,
                timeout=5
            )
            
            await self.update_device_status(device.id, is_online)
            return is_online
            
        except Exception as e:
            logger.error(f"Error checking device {device.id} ({device.ip_address}): {e}")
            await self.update_device_status(device.id, False)
            return False
    
    async def update_device_status(self, device_id: int, is_online: bool):
        """Update device status and last_seen timestamp."""
        from device_service.repositories.device_repository import DeviceRepository
        
        repo = DeviceRepository(self.db)
        
        status = DeviceStatus.ONLINE if is_online else DeviceStatus.OFFLINE
        last_seen = datetime.utcnow() if is_online else None
        
        await repo.update_device_status(
            device_id=device_id,
            status=status,
            last_seen=last_seen
        )
        
        await self.db.commit()
```

### Dependencies

- Task 034 (Connection test API - connection service exists)
- Task 027 (Device model must exist)

## Visual Testing

### Before State
- No automatic health checking
- Device status must be updated manually

### After State
- Devices checked automatically
- Status updated periodically
- Last_seen timestamps updated

### Testing Steps

1. Start health check service
2. Verify devices checked periodically
3. Verify status updates correctly
4. Verify last_seen timestamps update
5. Test with offline device
6. Stop health check service

## Definition of Done

- [x] Code written and follows standards
- [x] Health check service implemented
- [x] Periodic checking works
- [x] Status updates correctly
- [x] Handles errors gracefully
- [x] Logging implemented
- [x] Configurable interval works
- [x] Simulation mode support
- [x] Unit tests written and passing
- [x] Code reviewed

## Time Estimate

5-6 hours

## Notes

- Should run as background task (Celery or asyncio background task)
- Default interval: 5 minutes (configurable)
- Connection timeout: 5 seconds
- Concurrent checking for performance
- Respects simulation mode (random online/offline)
- Consider exponential backoff for frequently offline devices (future enhancement)

