"""Service for device connection operations."""

from typing import Optional
from device_service.core.config import settings


class DeviceConnectionService:
    """Service for device connection operations."""
    
    def __init__(self):
        """Initialize device connection service."""
        pass
    
    async def test_connection(
        self,
        ip_address: str,
        port: int,
        timeout: int = 5
    ) -> bool:
        """
        Test basic TCP connection to device.
        
        Args:
            ip_address: Device IP address
            port: Device port
            timeout: Connection timeout in seconds
        
        Returns:
            True if connection successful, False otherwise
        """
        import asyncio
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip_address, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False

