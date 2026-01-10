"""Service for device health checking and monitoring."""

import asyncio
import logging
import random
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from device_service.models.device import Device, DeviceStatus
from device_service.services.device_connection import DeviceConnectionService
from device_service.services.device_status_broadcaster import broadcaster
from device_service.repositories.device_repository import DeviceRepository
from device_service.core.config import settings
from device_service.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class DeviceHealthCheckService:
    """Background service for checking device connectivity."""
    
    def __init__(self):
        """Initialize health check service."""
        self.connection_service = DeviceConnectionService()
        self.running = False
        self.check_interval = settings.DEVICE_HEALTH_CHECK_INTERVAL
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the health check service."""
        if self.running:
            logger.warning("Health check service already running")
            return
        
        self.running = True
        logger.info(f"Starting device health check service (interval: {self.check_interval}s)")
        
        # Start background task
        self._task = asyncio.create_task(self._run_health_checks())
    
    async def stop(self):
        """Stop the health check service."""
        if not self.running:
            return
        
        logger.info("Stopping device health check service")
        self.running = False
        
        # Cancel the background task
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Device health check service stopped")
    
    async def _run_health_checks(self):
        """Main health check loop."""
        while self.running:
            try:
                await self.check_all_devices()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check cycle: {e}", exc_info=True)
            
            if self.running:
                try:
                    await asyncio.sleep(self.check_interval)
                except asyncio.CancelledError:
                    break
    
    async def check_all_devices(self):
        """Check connectivity for all active devices."""
        # Create a new database session for this check cycle
        async with AsyncSessionLocal() as db:
            try:
                repository = DeviceRepository(db)
                devices = await repository.get_all_active_devices()
                
                if not devices:
                    logger.debug("No active devices to check")
                    return
                
                logger.info(f"Checking {len(devices)} devices")
                
                # Check devices concurrently
                tasks = [self.check_device(device, db) for device in devices]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log summary
                online_count = sum(1 for r in results if r is True)
                offline_count = sum(1 for r in results if r is False)
                error_count = sum(1 for r in results if isinstance(r, Exception))


                logger.info(
                    f"Health check complete: {online_count} online, "
                    f"{offline_count} offline, {error_count} errors"
                )
            except Exception as e:
                logger.error(f"Error checking all devices: {e}", exc_info=True)
    
    async def check_device(self, device: Device, db: AsyncSession) -> bool:
        """
        Check connectivity for a single device.
        
        Args:
            device: Device instance to check
            db: Database session
        
        Returns:
            True if device is online, False otherwise
        """
        try:
            # Skip simulation mode devices (handled separately)
            if settings.SIMULATION_MODE:
                # In simulation mode, simulate random online/offline (90% online rate)
                is_online = random.random() > 0.1
                await self.update_device_status(device.id, is_online, db)
                return is_online
            
            # Test TCP connection
            success = await self.connection_service.test_connection(
                ip_address=device.ip_address,
                port=device.port,
                timeout=settings.DEFAULT_DEVICE_TIMEOUT
            )
            
            await self.update_device_status(device.id, success, db)
            return success
            
        except Exception as e:
            logger.error(
                f"Error checking device {device.id} ({device.ip_address}:{device.port}): {e}"
            )
            await self.update_device_status(device.id, False, db)
            return False
    
    async def update_device_status(self, device_id: int, is_online: bool, db: AsyncSession):
        """
        Update device status and last_seen timestamp, and broadcast update via WebSocket.
        
        Args:
            device_id: Device ID
            is_online: Whether device is online
            db: Database session
        """
        try:
            repository = DeviceRepository(db)
            
            # Get device to retrieve school_id for broadcasting
            device = await repository.get_by_id(device_id)
            if not device:
                logger.warning(f"Device {device_id} not found for status update")
                return
            
            status = DeviceStatus.ONLINE if is_online else DeviceStatus.OFFLINE
            last_seen = datetime.utcnow() if is_online else None
            
            await repository.update_device_status(
                device_id=device_id,
                status=status,
                last_seen=last_seen
            )
            
            logger.debug(
                f"Updated device {device_id}: status={status.value}, "
                f"last_seen={last_seen}"
            )
            
            # Broadcast status update via WebSocket
            try:
                await broadcaster.broadcast_device_status(
                    school_id=device.school_id,
                    device_id=device_id,
                    status=status.value,
                    last_seen=last_seen,
                )
            except Exception as e:
                # Log but don't fail the status update if broadcasting fails
                logger.warning(f"Failed to broadcast device status update: {e}")
                
        except Exception as e:
            logger.error(f"Error updating device {device_id} status: {e}", exc_info=True)

