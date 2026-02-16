"""Service for fetching device information from real ZKTeco devices."""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from device_service.models.device import Device
from device_service.services.device_connection import DeviceConnectionService
from device_service.repositories.device_repository import DeviceRepository

logger = logging.getLogger(__name__)


class DeviceInfoService:
    """Service for fetching device information from real ZKTeco devices."""

    def __init__(self, db: AsyncSession, connection_service: Optional[DeviceConnectionService] = None):
        """
        Initialize device info service.
        
        Args:
            db: Database session
            connection_service: Optional connection service (creates new if not provided)
        """
        self.db = db
        self.repository = DeviceRepository(db)
        self.connection_service = connection_service or DeviceConnectionService(db)

    async def fetch_device_serial(self, device: Device, update_database: bool = True) -> Optional[str]:
        """
        Fetch device serial number from real device.
        
        Args:
            device: Device model instance
            update_database: Whether to update device record in database (default: True)
        
        Returns:
            Serial number string or None if unavailable
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.error(f"Cannot connect to device {device.id} ({device.ip_address}:{device.port}) to fetch serial")
            return None

        try:
            # Fetch serial number from device
            serial = await conn.get_serial_number()

            if serial:
                # Clean and validate serial number
                serial = serial.strip()
                
                logger.info(
                    f"Fetched serial number '{serial}' from device {device.id} "
                    f"({device.ip_address}:{device.port})"
                )
                
                # Update device in database if requested
                if update_database:
                    device.serial_number = serial
                    await self.db.commit()
                    await self.db.refresh(device)
                    logger.debug(f"Updated device {device.id} serial_number in database")

            return serial
        except Exception as e:
            logger.error(
                f"Error fetching serial number from device {device.id} "
                f"({device.ip_address}:{device.port}): {e}",
                exc_info=True
            )
            return None

    async def fetch_device_name(self, device: Device) -> Optional[str]:
        """
        Fetch device name/model from real device.
        
        Args:
            device: Device model instance
        
        Returns:
            Device name string or None if unavailable
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.error(f"Cannot connect to device {device.id} to fetch device name")
            return None

        try:
            name = await conn.get_device_name()
            if name:
                logger.debug(f"Fetched device name '{name}' from device {device.id}")
            return name
        except Exception as e:
            logger.error(f"Error fetching device name from device {device.id}: {e}")
            return None

    async def fetch_device_firmware(self, device: Device) -> Optional[str]:
        """
        Fetch firmware version from real device.
        
        Args:
            device: Device model instance
        
        Returns:
            Firmware version string or None if unavailable
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.error(f"Cannot connect to device {device.id} to fetch firmware")
            return None

        try:
            firmware = await conn.get_firmware_version()
            if firmware:
                logger.debug(f"Fetched firmware version '{firmware}' from device {device.id}")
            return firmware
        except Exception as e:
            logger.error(f"Error fetching firmware from device {device.id}: {e}")
            return None

    async def fetch_device_time(self, device: Device) -> Optional[str]:
        """
        Fetch device current time from real device.
        
        Args:
            device: Device model instance
        
        Returns:
            Device time as ISO 8601 string or None if unavailable
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.error(f"Cannot connect to device {device.id} to fetch time")
            return None

        try:
            device_time = await conn.get_time()
            if device_time:
                logger.debug(f"Fetched device time '{device_time}' from device {device.id}")
            return device_time  # Already converted to string in base.py
        except Exception as e:
            logger.error(f"Error fetching time from device {device.id}: {e}", exc_info=True)
            return None

    async def fetch_device_capacity(self, device: Device) -> Optional[Dict[str, int]]:
        """
        Fetch device capacity information from real device.
        
        Args:
            device: Device model instance
        
        Returns:
            Dictionary with capacity info including:
            - users, fingers, records, cards, faces (current counts)
            - users_cap, fingers_cap, rec_cap, faces_cap (maximum capacities)
            - users_av, fingers_av, rec_av (available/free slots)
            or None if unavailable
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.error(f"Cannot connect to device {device.id} to fetch capacity")
            return None

        try:
            capacity = await conn.get_free_sizes()
            if capacity:
                logger.debug(f"Fetched capacity from device {device.id}: {capacity}")
            return capacity
        except Exception as e:
            logger.error(f"Error fetching capacity from device {device.id}: {e}")
            return None

    async def fetch_all_device_info(self, device: Device, update_serial: bool = True) -> Dict[str, Any]:
        """
        Fetch all available device information at once.
        
        Args:
            device: Device model instance
            update_serial: Whether to update serial number in database (default: True)
        
        Returns:
            Dictionary with all device information
        """
        info = {}

        # Fetch all info (can be done in parallel if needed)
        serial = await self.fetch_device_serial(device, update_database=update_serial)
        name = await self.fetch_device_name(device)
        firmware = await self.fetch_device_firmware(device)
        device_time = await self.fetch_device_time(device)
        capacity = await self.fetch_device_capacity(device)

        info.update({
            "serial_number": serial,
            "device_name": name,
            "firmware_version": firmware,
            "device_time": device_time,
            "capacity": capacity,
        })

        return info

    async def fetch_attendance_logs(self, device: Device) -> List[Dict[str, Any]]:
        """
        Fetch attendance logs from the device.

        Returns a list of normalized dicts per record:
        - user_id: str
        - timestamp: datetime
        - punch: int or None
        - device_serial: str or None

        Returns empty list if device is offline or on error (graceful, no raise).
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.warning(f"Cannot connect to device {device.id} to fetch attendance logs")
            return []

        try:
            logs = await conn.get_attendance_logs()
            logger.debug(f"Fetched {len(logs)} attendance logs from device {device.id}")
            return logs
        except Exception as e:
            logger.error(
                f"Error fetching attendance logs from device {device.id}: {e}",
                exc_info=True,
            )
            return []
