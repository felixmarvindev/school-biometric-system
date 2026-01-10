"""
ZKTeco device connection wrapper.

This module provides async wrappers around the pyzk library for non-blocking
device communication. The pyzk library is synchronous, so we wrap it with
asyncio.to_thread to make it async-compatible.
"""

import asyncio
import logging
from typing import Optional, Any, Dict
from zk import ZK

# pyzk exception handling - import from zk.exception module
# Library defines: ZKError (base), ZKErrorConnection, ZKErrorResponse, ZKNetworkError
try:
    from zk.exception import (
        ZKError,
        ZKErrorConnection,
        ZKErrorResponse,
        ZKNetworkError,
    )
except ImportError:
    # Fallback if exception module not available (shouldn't happen with pyzk)
    # Define minimal exceptions to prevent crashes
    class ZKError(Exception):
        pass
    
    class ZKErrorConnection(ZKError):
        pass
    
    class ZKErrorResponse(ZKError):
        pass
    
    class ZKNetworkError(ZKError):
        pass

from device_service.zk.const import DEFAULT_PORT, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class ZKDeviceConnection:
    """
    Async wrapper for ZKTeco device connections.
    
    This class wraps the pyzk ZK library to provide async/await compatible
    device communication. All blocking operations are run in a thread pool
    using asyncio.to_thread.
    
    Example:
        ```python
        async with ZKDeviceConnection("192.168.1.100", 4370) as device:
            if device.is_connected:
                users = await device.get_users()
                print(f"Device has {len(users)} users")
        ```
    """
    
    def __init__(
        self,
        ip: str,
        port: int = DEFAULT_PORT,
        password: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT,
        ommit_ping: bool = False,
    ):
        """
        Initialize ZKTeco device connection.
        
        Args:
            ip: Device IP address
            port: Device port (default: 4370)
            password: Device communication password (optional, default: 0)
            timeout: Connection timeout in seconds (default: 5)
            ommit_ping: Skip ping during connection (default: False)
        """
        self.ip = ip
        self.port = port
        self.password = password or 0
        self.timeout = timeout
        self.ommit_ping = ommit_ping
        
        # Initialize ZK instance (doesn't connect yet)
        self.zk = ZK(
            ip,
            port=port,
            timeout=timeout,
            password=self.password,
            ommit_ping=ommit_ping,
        )
        # After connection, conn is the ZK instance (zk.connect() returns self)
        # Using Optional[Any] to allow accessing methods without type errors,
        # but any non-existent methods will raise AttributeError at runtime
        self.conn: Optional[ZK] = None
        self._is_connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self._is_connected and self.conn is not None
    
    async def connect(self) -> bool:
        """
        Establish connection to device (async wrapper).
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            logger.warning(f"Device {self.ip}:{self.port} already connected")
            return True
        
        try:
            logger.info(f"Attempting to connect to device {self.ip}:{self.port}")
            # Run blocking connect in thread pool
            self.conn = await asyncio.to_thread(self.zk.connect)
            
            if self.conn:
                self._is_connected = True
                logger.info(f"Successfully connected to device {self.ip}:{self.port}")
                return True
            else:
                logger.error(f"Connection to {self.ip}:{self.port} returned None")
                return False
                
        except ZKErrorConnection as e:
            logger.error(f"Connection error to {self.ip}:{self.port}: {e}")
            self._is_connected = False
            self.conn = None
            return False
        except ZKNetworkError as e:
            logger.error(f"Network error connecting to {self.ip}:{self.port}: {e}")
            self._is_connected = False
            self.conn = None
            return False
        except ZKError as e:
            logger.error(f"ZKTeco error connecting to {self.ip}:{self.port}: {e}")
            self._is_connected = False
            self.conn = None
            return False
        except Exception as e:
            logger.exception(f"Unexpected error connecting to {self.ip}:{self.port}: {e}")
            self._is_connected = False
            self.conn = None
            return False
    
    async def disconnect(self):
        """Disconnect from device."""
        if not self.conn:
            return
        
        try:
            logger.info(f"Disconnecting from device {self.ip}:{self.port}")
            await asyncio.to_thread(self.conn.disconnect)
            logger.info(f"Disconnected from device {self.ip}:{self.port}")
        except Exception as e:
            logger.error(f"Error disconnecting from {self.ip}:{self.port}: {e}")
        finally:
            self.conn = None
            self._is_connected = False
    
    async def get_serial_number(self) -> Optional[str]:
        """
        Get device serial number using pyzk's get_serialnumber() method.
        
        Returns:
            Serial number string or None if unavailable/error
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: get_serialnumber() returns str or raises ZKErrorResponse
            serial = await asyncio.to_thread(self.conn.get_serialnumber)
            return str(serial).strip() if serial else None
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method get_serialnumber not found on device {self.ip}:{self.port}: {e}")
            return None
        except ZKError as e:
            # Device returned error response
            logger.warning(f"Error getting serial number from {self.ip}:{self.port}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting serial number from {self.ip}:{self.port}: {e}")
            return None
    
    async def get_device_name(self) -> Optional[str]:
        """
        Get device name/model using pyzk's get_device_name() method.
        
        Note: pyzk's get_device_name() returns empty string "" on error, not None.
        
        Returns:
            Device name string or None if unavailable/error
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: get_device_name() returns str (empty string on error)
            name = await asyncio.to_thread(self.conn.get_device_name)
            # pyzk returns "" on error, convert to None
            return str(name).strip() if name and name.strip() else None
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method get_device_name not found on device {self.ip}:{self.port}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error getting device name from {self.ip}:{self.port}: {e}")
            return None
    
    async def get_firmware_version(self) -> Optional[str]:
        """
        Get device firmware version using pyzk's get_firmware_version() method.
        
        Returns:
            Firmware version string or None if unavailable/error
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: get_firmware_version() returns str or raises ZKErrorResponse
            version = await asyncio.to_thread(self.conn.get_firmware_version)
            return str(version).strip() if version else None
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method get_firmware_version not found on device {self.ip}:{self.port}: {e}")
            return None
        except ZKError as e:
            # Device returned error response
            logger.warning(f"Error getting firmware version from {self.ip}:{self.port}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting firmware version from {self.ip}:{self.port}: {e}")
            return None
    
    async def get_time(self) -> Optional[str]:
        """
        Get device current time using pyzk's get_time() method.
        
        Note: pyzk's get_time() returns a datetime object.
        
        Returns:
            Device time as ISO 8601 string or None if unavailable/error
        """
        from datetime import datetime
        
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: get_time() returns datetime or raises ZKErrorResponse
            device_time: datetime = await asyncio.to_thread(self.conn.get_time)
            
            if device_time:
                # pyzk returns datetime object, convert to ISO 8601 string
                if isinstance(device_time, datetime):
                    return device_time.isoformat()
                # Fallback if it's somehow a string already
                return str(device_time) if device_time else None
            
            return None
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method get_time not found on device {self.ip}:{self.port}: {e}")
            return None
        except ZKError as e:
            # Device returned error response
            logger.warning(f"Error getting time from {self.ip}:{self.port}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting time from {self.ip}:{self.port}: {e}")
            return None
    
    async def get_free_sizes(self) -> Optional[Dict[str, int]]:
        """
        Get device capacity information using pyzk's read_sizes() method.
        
        read_sizes() reads memory usage and sets attributes directly on the
        connection object (self.conn). After calling read_sizes(), these attributes
        are available on self.conn:
        - users: Current number of users
        - fingers: Current number of fingerprints
        - records: Current number of attendance records
        - cards: Current number of cards
        - faces: Current number of faces (if supported)
        - users_cap: Maximum users capacity
        - fingers_cap: Maximum fingerprints capacity
        - rec_cap: Maximum records capacity
        - faces_cap: Maximum faces capacity
        - users_av: Available users slots
        - fingers_av: Available fingerprints slots
        - rec_av: Available records slots
        
        Returns:
            Dictionary with capacity information or None if unavailable/error
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: read_sizes() returns True if successful,
            # raises ZKErrorResponse if failed, and sets attributes on self.conn
            success = await asyncio.to_thread(self.conn.read_sizes)
            
            if not success:
                logger.warning(f"read_sizes() returned False for device {self.ip}:{self.port}")
                return None
            
            # Extract capacity values from connection object attributes
            # These are set by read_sizes() method (see pyzk/base.py lines 664-679)
            # Using getattr with defaults in case attributes weren't set
            capacity_info: Dict[str, int] = {
                # Current usage
                "users": getattr(self.conn, 'users', 0),
                "fingers": getattr(self.conn, 'fingers', 0),
                "records": getattr(self.conn, 'records', 0),
                "cards": getattr(self.conn, 'cards', 0),
                "faces": getattr(self.conn, 'faces', 0),
                # Maximum capacity
                "users_cap": getattr(self.conn, 'users_cap', 0),
                "fingers_cap": getattr(self.conn, 'fingers_cap', 0),
                "rec_cap": getattr(self.conn, 'rec_cap', 0),
                "faces_cap": getattr(self.conn, 'faces_cap', 0),
                # Available (free) slots
                "users_av": getattr(self.conn, 'users_av', 0),
                "fingers_av": getattr(self.conn, 'fingers_av', 0),
                "rec_av": getattr(self.conn, 'rec_av', 0),
            }
            
            logger.debug(
                f"Read sizes from device {self.ip}:{self.port} - "
                f"Users: {capacity_info['users']}/{capacity_info['users_cap']}, "
                f"Fingers: {capacity_info['fingers']}/{capacity_info['fingers_cap']}"
            )
            
            return capacity_info
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method read_sizes not found on device {self.ip}:{self.port}: {e}")
            return None
        except ZKError as e:
            # Device returned error response (ZKErrorResponse)
            logger.error(f"ZKError reading sizes from {self.ip}:{self.port}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading sizes from {self.ip}:{self.port}: {e}", exc_info=True)
            return None
    
    async def test_connection(self) -> bool:
        """
        Test if device connection is still active.
        
        Uses get_time() as a lightweight operation to verify connectivity.
        
        Returns:
            True if connection is active, False otherwise
        """
        if not self.is_connected or self.conn is None:
            return False
        
        try:
            # Use get_time() as a lightweight operation to test connection
            # If connection is dead, this will raise an exception
            await asyncio.to_thread(self.conn.get_time)
            return True
        except (ZKError, ZKErrorConnection, ZKNetworkError, AttributeError) as e:
            # Connection is dead or method doesn't exist
            logger.debug(f"Connection test failed for {self.ip}:{self.port}: {e}")
            self._is_connected = False
            return False
        except Exception as e:
            # Unexpected error - assume connection is dead
            logger.warning(f"Unexpected error testing connection for {self.ip}:{self.port}: {e}")
            self._is_connected = False
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        return False  # Don't suppress exceptions
