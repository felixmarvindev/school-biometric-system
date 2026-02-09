"""
ZKTeco device connection wrapper.

This module provides async wrappers around the pyzk library for non-blocking
device communication. The pyzk library is synchronous, so we wrap it with
asyncio.to_thread to make it async-compatible.
"""

import asyncio
import logging
import time
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

    async def get_enrolled_finger_ids(self, user_id: str) -> list[int]:
        """
        Get list of finger IDs (0-9) that have templates enrolled for this user on the device.

        Args:
            user_id: User ID string on device (e.g. str(student_id))

        Returns:
            List of finger indices that have enrolled templates
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")

        enrolled: list[int] = []
        try:
            for finger_id in range(10):
                try:
                    templ = await asyncio.to_thread(
                        self.conn.get_user_template,
                        uid=None,
                        temp_id=finger_id,
                        user_id=user_id,
                    )
                    if templ is not None and getattr(templ, "template", None):
                        enrolled.append(finger_id)
                except Exception:
                    continue
            return enrolled
        except Exception as e:
            logger.warning(f"get_enrolled_finger_ids failed for {self.ip}:{self.port}: {e}")
            return []

    async def finger_is_enrolled(self, user_id: str, finger_id: int) -> bool:
        """
        Check if the given finger has an enrolled template for this user on the device.

        Args:
            user_id: User ID string on device
            finger_id: Finger index (0-9)

        Returns:
            True if template exists, False otherwise
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")

        try:
            templ = await asyncio.to_thread(
                self.conn.get_user_template,
                uid=None,
                temp_id=finger_id,
                user_id=user_id,
            )
            return templ is not None and bool(getattr(templ, "template", None))
        except Exception as e:
            logger.debug(f"finger_is_enrolled check failed: {e}")
            return False

    async def get_template_bytes(self, user_id: str, finger_id: int) -> Optional[bytes]:
        """
        Get fingerprint template bytes from device for storage/sync.

        Args:
            user_id: User ID string on device (e.g. str(student_id))
            finger_id: Finger index (0-9)

        Returns:
            Template bytes or None if not found/error
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")

        try:
            templ = await asyncio.to_thread(
                self.conn.get_user_template,
                uid=None,
                temp_id=finger_id,
                user_id=user_id,
            )
            if templ is None:
                return None
            template = getattr(templ, "template", None)
            if template is None or not isinstance(template, (bytes, bytearray)):
                return None
            return bytes(template)
        except Exception as e:
            logger.warning(f"get_template_bytes failed for {self.ip}:{self.port}: {e}")
            return None

    async def delete_user_template(
        self,
        user_id: str,
        finger_id: int,
        uid: Optional[int] = None,
    ) -> bool:
        """
        Delete the fingerprint template for the given user and finger on the device.

        Args:
            user_id: User ID string on device
            finger_id: Finger index (0-9)
            uid: Optional device UID (resolved from get_users by user_id if not provided)

        Returns:
            True if delete succeeded, False otherwise
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")

        try:
            if uid is None:
                users = await asyncio.to_thread(self.conn.get_users)
                users = [u for u in (users or []) if getattr(u, "user_id", None) == user_id]
                if not users:
                    logger.warning(f"User {user_id} not found on device for delete_user_template")
                    return False
                uid = users[0].uid

            await asyncio.to_thread(
                self.conn.delete_user_template,
                uid=uid,
                temp_id=finger_id,
                user_id="",
            )
            logger.info(f"Deleted template user_id={user_id} finger_id={finger_id} on {self.ip}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"delete_user_template failed: {e}", exc_info=True)
            return False

    async def start_enrollment(self, user_id: int, finger_id: int = 0) -> bool:
        """
        Start fingerprint enrollment mode on device.
        
        This puts the device in enrollment mode and waits for the user to place their finger.
        The device will capture the fingerprint template when the user places their finger.
        
        Note: This method sends CMD_STARTENROLL command directly without waiting for capture.
        The actual fingerprint capture and events will be handled asynchronously via event polling.
        
        Args:
            user_id: User ID on the device (typically matches student ID)
            finger_id: Finger index (0-9, default: 0 for right thumb)
            
        Returns:
            True if enrollment command sent successfully, False otherwise
            
        Raises:
            RuntimeError: If device is not connected
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # Import struct for packing command string
            from struct import pack
            
            # First, cancel any previous capture
            await asyncio.to_thread(self.conn.cancel_capture)
            
            # Send CMD_STARTENROLL command directly
            # We replicate the logic from enroll_user() but without waiting for events
            # Command format depends on TCP/UDP mode
            command = 61  # CMD_STARTENROLL
            user_id_str = str(user_id)
            
            if self.conn.tcp:
                # TCP mode: pack('<24sbb', user_id, temp_id, 1)
                command_string = pack('<24sbb', user_id_str.encode('utf-8')[:24].ljust(24, b'\x00'), finger_id, 1)
            else:
                # UDP mode: pack('<Ib', int(user_id), temp_id)
                command_string = pack('<Ib', int(user_id), finger_id)
            
            # Access the private __send_command method using name mangling
            # In Python, __method becomes _ClassName__method
            # Since the class is named ZK, __send_command becomes _ZK__send_command
            cmd_response = await asyncio.to_thread(
                self.conn._ZK__send_command,  # Access private method via name mangling
                command,
                command_string
            )
            
            if cmd_response and cmd_response.get('status'):
                logger.info(
                    f"Started enrollment on device {self.ip}:{self.port} - "
                    f"user_id={user_id}, finger_id={finger_id}"
                )
                return True
            else:
                logger.warning(
                    f"Enrollment start command failed on device {self.ip}:{self.port} - "
                    f"user_id={user_id}, finger_id={finger_id}, response={cmd_response}"
                )
                return False
            
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method or attribute not found on device {self.ip}:{self.port}: {e}")
            return False
        except ZKError as e:
            # Device returned error response
            logger.error(f"ZKError starting enrollment on {self.ip}:{self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error starting enrollment on {self.ip}:{self.port}: {e}", exc_info=True)
            return False
    
    async def cancel_enrollment(self) -> bool:
        """
        Cancel ongoing fingerprint enrollment.
        
        This sends CMD_CANCELCAPTURE command to cancel any active enrollment session.
        
        Returns:
            True if cancel command sent successfully, False otherwise
            
        Raises:
            RuntimeError: If device is not connected
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: cancel_capture()
            # This sends CMD_CANCELCAPTURE command to device
            success = await asyncio.to_thread(self.conn.cancel_capture)
            
            if success:
                logger.info(f"Cancelled enrollment on device {self.ip}:{self.port}")
            else:
                logger.warning(f"Enrollment cancel returned False on device {self.ip}:{self.port}")
            
            return bool(success)
            
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method cancel_capture not found on device {self.ip}:{self.port}: {e}")
            return False
        except ZKError as e:
            # Device returned error response
            logger.error(f"ZKError cancelling enrollment on {self.ip}:{self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error cancelling enrollment on {self.ip}:{self.port}: {e}", exc_info=True)
            return False
    
    async def poll_enrollment_events(
        self,
        callback=None,
        timeout: int = 60,
        max_attempts: int = 3,
    ):
        """
        Poll for enrollment events and report progress via callback.
        
        Based on enroll_user() logic, this method listens for enrollment events:
        - First event: Finger placement detected (33% progress)
        - Second event: Capturing/processing (66% progress)
        - Final event: Completion (100% progress or error)
        
        Args:
            callback: Optional callback function(event_type, progress, status, message)
                     Called with: ('progress', 33, 'placing', 'Place finger...')
                     Or: ('complete', 100, 'complete', 'Enrollment successful')
                     Or: ('error', 0, 'error', 'Error message')
            timeout: Socket timeout in seconds
            max_attempts: Maximum number of enrollment attempts (default 3)
            
        Returns:
            dict with 'success' (bool), 'progress' (int), 'status' (str), 'message' (str)
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            from struct import unpack, error as struct_error
            from socket import timeout as SocketTimeout
            
            # Use pyzk name-mangled attributes (same as verify_test_2 / test_enrollment_direct)
            conn = self.conn
            original_timeout = conn._ZK__timeout
            conn._ZK__sock.settimeout(timeout)
            
            attempts = max_attempts
            progress = 0
            status = "placing"
            message = "Place your finger on the scanner"
            
            # Broadcast initial progress if callback provided
            if callback:
                await callback('progress', 0, 'ready', 'Enrollment started. Place your finger on the scanner.')
            
            while attempts > 0:
                try:
                    wait_start = time.monotonic()
                    # Wait for first event (finger placement)
                    logger.debug(f"Waiting for first enrollment event (attempt {attempts})...")
                    data_recv = await asyncio.to_thread(conn._ZK__sock.recv, 1032)
                    await asyncio.to_thread(conn._ZK__ack_ok)
                    
                    # Parse response code
                    if conn.tcp:
                        res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0] if len(data_recv) > 16 else -1
                    else:
                        res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0] if len(data_recv) > 8 else -1
                    
                    # Early termination (verify_test_2 approach): res 0 = success; res 4 = cancel; res 6 = timeout
                    # Use elapsed time to distinguish timeout (long wait) vs cancel (short) when res=4
                    if res == 0:
                        # Success on first event (device sent completion in one shot)
                        try:
                            conn._ZK__sock.settimeout(original_timeout)
                            await asyncio.to_thread(conn.reg_event, 0)
                            await asyncio.to_thread(conn.cancel_capture)
                        except Exception as e:
                            logger.warning("Cleanup after success: %s", e)
                        if callback:
                            await callback('complete', 100, 'complete', 'Enrollment completed successfully')
                        return {'success': True, 'progress': 100, 'status': 'complete', 'message': 'Enrollment completed successfully'}
                    if res == 6 or res == 4:
                        elapsed = time.monotonic() - wait_start
                        logger.debug(f"Early termination: res={res}, elapsed={elapsed:.1f}s")
                        cancel_msg = "Enrollment timeout" if (res == 6 or elapsed >= timeout - 5) else "Enrollment cancelled by device"
                        if callback:
                            await callback('error', 0, 'error', cancel_msg)
                        try:
                            conn._ZK__sock.settimeout(original_timeout)
                            await asyncio.to_thread(conn.reg_event, 0)
                            await asyncio.to_thread(conn.cancel_capture)
                        except Exception as e:
                            logger.warning("Cleanup after early term: %s", e)
                        return {'success': False, 'progress': progress, 'status': 'error', 'message': cancel_msg}
                    
                    # Broadcast finger placement detected (33%)
                    if callback:
                        await callback('progress', 33, 'placing', 'Finger detected. Keep your finger steady...')
                    
                    # Wait for second event (capturing)
                    logger.debug("Waiting for second enrollment event...")
                    data_recv = await asyncio.to_thread(conn._ZK__sock.recv, 1032)
                    await asyncio.to_thread(conn._ZK__ack_ok)
                    
                    if conn.tcp:
                        res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0] if len(data_recv) > 16 else -1
                    else:
                        res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0] if len(data_recv) > 8 else -1
                    
                    if res == 6 or res == 4:
                        elapsed = time.monotonic() - wait_start
                        msg = "Enrollment timeout" if (res == 6 or elapsed >= timeout - 5) else "Enrollment cancelled by device"
                        if callback:
                            await callback('error', 0, 'error', msg)
                        try:
                            conn._ZK__sock.settimeout(original_timeout)
                            await asyncio.to_thread(conn.reg_event, 0)
                            await asyncio.to_thread(conn.cancel_capture)
                        except Exception as e:
                            logger.warning("Cleanup: %s", e)
                        return {'success': False, 'progress': progress, 'status': 'error', 'message': msg}
                    elif res == 0x64:  # 100 - low quality, retry
                        logger.debug("Finger quality low, trying again...")
                        attempts -= 1
                        if callback:
                            await callback('progress', 66, 'processing', f'Finger quality low. Attempt {max_attempts - attempts + 1}/{max_attempts}.')
                        continue
                    
                    # Broadcast capturing progress (66%)
                    if callback:
                        await callback('progress', 66, 'capturing', 'Capturing fingerprint data...')
                    
                    # Final event (completion) - same packet flow as verify_test_2 / test_enrollment_direct
                    logger.debug("Waiting for final event (completion)...")
                    data_recv = await asyncio.to_thread(conn._ZK__sock.recv, 1032)
                    await asyncio.to_thread(conn._ZK__ack_ok)
                    
                    if conn.tcp:
                        res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0] if len(data_recv) > 16 else -1
                    else:
                        res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0] if len(data_recv) > 8 else -1
                    
                    # Success: known errors only 4,5,6. Many devices return 46,50,54,55 etc for success.
                    if res not in (4, 5, 6):
                        try:
                            size = unpack("H", data_recv.ljust(16, b"\x00")[10:12])[0]
                            pos = unpack("H", data_recv.ljust(16, b"\x00")[12:14])[0]
                            msg = f"Enrollment completed successfully (size={size}, pos={pos})"
                        except (IndexError, struct_error):
                            msg = "Enrollment completed successfully"
                        try:
                            conn._ZK__sock.settimeout(original_timeout)
                            await asyncio.to_thread(conn.reg_event, 0)
                            await asyncio.to_thread(conn.cancel_capture)
                        except Exception as e:
                            logger.warning("Cleanup after success: %s", e)
                        if callback:
                            await callback('complete', 100, 'complete', msg)
                        return {'success': True, 'progress': 100, 'status': 'complete', 'message': msg}
                    if res == 5:
                        msg = "This fingerprint is already enrolled"
                        if callback:
                            await callback('error', 0, 'error', msg)
                        return {'success': False, 'progress': 0, 'status': 'error', 'message': msg}
                    # res 4 or 6
                    msg = "Enrollment timeout"
                    if callback:
                        await callback('error', 0, 'error', msg)
                    return {'success': False, 'progress': 0, 'status': 'error', 'message': msg}
                    
                except SocketTimeout:
                    logger.warning("Timeout waiting for enrollment event")
                    if callback:
                        await callback('error', 0, 'error', 'Enrollment timeout. Please try again.')
                    return {'success': False, 'progress': progress, 'status': 'error', 'message': 'Enrollment timeout'}
                except Exception as e:
                    logger.error(f"Error polling enrollment event: {e}", exc_info=True)
                    if callback:
                        await callback('error', 0, 'error', f'Error during enrollment: {str(e)}')
                    return {'success': False, 'progress': progress, 'status': 'error', 'message': str(e)}
            
            # Final event when attempts exhausted (low-quality retries)
            if attempts == 0:
                try:
                    logger.debug("Waiting for final enrollment event...")
                    data_recv = await asyncio.to_thread(conn._ZK__sock.recv, 1032)
                    await asyncio.to_thread(conn._ZK__ack_ok)
                    if conn.tcp:
                        res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0]
                    else:
                        res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0]
                    if res not in (4, 5, 6):
                        try:
                            size = unpack("H", data_recv.ljust(16, b"\x00")[10:12])[0]
                            pos = unpack("H", data_recv.ljust(16, b"\x00")[12:14])[0]
                            message = f"Enrollment completed successfully (size={size}, pos={pos})"
                        except (IndexError, struct_error):
                            message = "Enrollment completed successfully"
                        try:
                            conn._ZK__sock.settimeout(original_timeout)
                            await asyncio.to_thread(conn.reg_event, 0)
                            await asyncio.to_thread(conn.cancel_capture)
                        except Exception as e:
                            logger.warning("Cleanup after success: %s", e)
                        if callback:
                            await callback('complete', 100, 'complete', message)
                        return {'success': True, 'progress': 100, 'status': 'complete', 'message': message}
                    if res == 5:
                        message = "This fingerprint is already enrolled"
                        if callback:
                            await callback('error', 0, 'error', message)
                        return {'success': False, 'progress': 0, 'status': 'error', 'message': message}
                    message = "Enrollment timeout"
                    if callback:
                        await callback('error', 0, 'error', message)
                    return {'success': False, 'progress': 0, 'status': 'error', 'message': message}
                except SocketTimeout:
                    if callback:
                        await callback('error', 0, 'error', 'Enrollment timeout')
                    return {'success': False, 'progress': 0, 'status': 'error', 'message': 'Enrollment timeout'}
                except Exception as e:
                    logger.error("Error waiting for enrollment completion: %s", e, exc_info=True)
                    if callback:
                        await callback('error', 0, 'error', str(e))
                    return {'success': False, 'progress': 0, 'status': 'error', 'message': str(e)}
            
            try:
                conn._ZK__sock.settimeout(original_timeout)
                await asyncio.to_thread(conn.reg_event, 0)
                await asyncio.to_thread(conn.cancel_capture)
            except Exception as e:
                logger.warning("Cleanup: %s", e)
            return {'success': False, 'progress': progress, 'status': 'error', 'message': 'Enrollment failed'}
            
        except Exception as e:
            logger.error(f"Unexpected error polling enrollment events: {e}", exc_info=True)
            if callback:
                await callback('error', 0, 'error', f'Unexpected error: {str(e)}')
            return {'success': False, 'progress': 0, 'status': 'error', 'message': str(e)}
    
    async def enroll_user_async(
        self,
        user_id: str,
        finger_id: int = 0,
        uid: int = 0,
        progress_callback=None,
        timeout: int = 60,
        max_attempts: int = 3,
    ):
        """
        Run full enrollment flow using verified AsyncBiometricEnrollment logic.

        This aligns with verify_test_2 - emits rich events (STARTED, WAITING_FINGER,
        FINGER_DETECTED, FINGER_PROCESSED, ATTEMPT_COMPLETED, COMPLETED, etc.)
        via progress_callback for UI broadcasting.

        Args:
            user_id: User ID string on device (e.g. student_id as string)
            finger_id: Finger index (0-9)
            uid: User UID (used if user_id empty to resolve from device)
            progress_callback: Async callback(EnrollmentProgress) - receives all events
            timeout: Socket timeout in seconds
            max_attempts: Max finger scan attempts

        Returns:
            True if enrollment successful, False otherwise
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")

        from device_service.zk.enrollment import AsyncBiometricEnrollment

        enrollment = AsyncBiometricEnrollment(self.conn)
        return await enrollment.enroll_user_async(
            uid=uid,
            temp_id=finger_id,
            user_id=user_id,
            progress_callback=progress_callback,
            timeout=timeout,
            max_attempts=max_attempts,
        )

    async def register_event(self, event_flag: int) -> bool:
        """
        Register for real-time device events.
        
        This sends CMD_REG_EVENT command to register for specific event types.
        Common event flags:
        - EF_ATTLOG = 1 (attendance events)
        - EF_ENROLLFINGER = 8 (enrollment events)
        - EF_ALARM = 512 (alarm events)
        
        Args:
            event_flag: Event flag value (bitmask)
            
        Returns:
            True if event registration successful, False otherwise
            
        Raises:
            RuntimeError: If device is not connected
        """
        if not self.is_connected or self.conn is None:
            raise RuntimeError("Device not connected")
        
        try:
            # pyzk library method: reg_event(event_flag)
            # This sends CMD_REG_EVENT command to device
            success = await asyncio.to_thread(self.conn.reg_event, event_flag)
            
            if success:
                logger.debug(f"Registered for events (flag={event_flag}) on device {self.ip}:{self.port}")
            else:
                logger.warning(f"Event registration returned False on device {self.ip}:{self.port}")
            
            return bool(success)
            
        except AttributeError as e:
            # Method doesn't exist on connection object
            logger.error(f"Method reg_event not found on device {self.ip}:{self.port}: {e}")
            return False
        except ZKError as e:
            # Device returned error response
            logger.error(f"ZKError registering events on {self.ip}:{self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error registering events on {self.ip}:{self.port}: {e}", exc_info=True)
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        return False  # Don't suppress exceptions
