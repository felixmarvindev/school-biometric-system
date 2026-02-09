#!/usr/bin/env python3
"""
Standalone ZKTeco fingerprint enrollment test script.

Uses pyzk library directly - NO imports from device_service.
Copy all logic here, verify it works, then port back to the main library.

Usage (from project root, with venv activated):
    python backend/device_service/test_enrollment_direct.py

Device config (edit constants below):
    IP: 192.168.0.121, Port: 4370, User ID: 1, Finger: 0 (right thumb)
"""

import sys
from pathlib import Path

# Ensure we import pyzk's zk, not local device_service/zk/
# Script dir (backend/device_service/) shadows pyzk - remove it from path
_script_dir = str(Path(__file__).resolve().parent)
if _script_dir in sys.path:
    sys.path.remove(_script_dir)

import asyncio
from enum import Enum
from typing import Callable, Optional, Awaitable
from struct import pack, unpack
import codecs

from zk import ZK, const
DEVICE_IP = "192.168.0.121"
DEVICE_PORT = 4370
DEVICE_PASSWORD = None
USER_ID = '3'
FINGER_ID = 1  # 0 = right thumb

class EnrollmentEvent(Enum):
    """Enumeration of enrollment progress events"""
    STARTED = "started"
    WAITING_FINGER = "waiting_finger"
    FINGER_DETECTED = "finger_detected"
    FINGER_PROCESSED = "finger_processed"
    ATTEMPT_COMPLETED = "attempt_completed"
    DUPLICATE_FINGER = "duplicate_finger"
    TIMEOUT = "timeout"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnrollmentProgress:
    """Data class for enrollment progress information"""

    def __init__(self, event: EnrollmentEvent, attempt: int, total_attempts: int,
                 message: str = "", data: dict = None):
        self.event = event
        self.attempt = attempt
        self.total_attempts = total_attempts
        self.message = message
        self.data = data or {}
        self.timestamp = asyncio.get_event_loop().time()

    def to_dict(self):
        """Convert to dictionary for easy serialization"""
        return {
            'event': self.event.value,
            'attempt': self.attempt,
            'total_attempts': self.total_attempts,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp
        }


class AsyncBiometricEnrollment:
    """Async wrapper for ZK device enrollment with callback support"""

    def __init__(self, zk_instance):
        """
        Initialize with a ZK instance

        :param zk_instance: Connected ZK object
        """
        self.zk = zk_instance
        self._cancel_requested = False

    async def enroll_user_async(
            self,
            uid: int = 0,
            temp_id: int = 0,
            user_id: str = '',
            progress_callback: Optional[Callable[[EnrollmentProgress], Awaitable[None]]] = None,
            timeout: int = 60,
            max_attempts: int = 3
    ) -> bool:
        """
        Asynchronously enroll a user with progress callbacks

        :param uid: User UID
        :param temp_id: Template ID (finger index 0-9)
        :param user_id: User ID string
        :param progress_callback: Async callback function for progress updates
        :param timeout: Timeout in seconds for enrollment
        :param max_attempts: Maximum number of finger scan attempts (default 3)
        :return: True if enrollment successful, False otherwise
        """
        self._cancel_requested = False

        # Emit started event
        await self._emit_progress(
            EnrollmentEvent.STARTED,
            0,
            max_attempts,
            f"Starting enrollment for user {user_id or uid}, template {temp_id}",
            progress_callback
        )

        try:
            # Prepare enrollment
            if not user_id:
                users = await asyncio.to_thread(self.zk.get_users)
                users = list(filter(lambda x: x.uid == uid, users))
                if len(users) >= 1:
                    user_id = users[0].user_id
                else:
                    await self._emit_progress(
                        EnrollmentEvent.FAILED,
                        0,
                        max_attempts,
                        "User not found",
                        progress_callback
                    )
                    return False

            # Prepare command
            command = const.CMD_STARTENROLL
            if self.zk.tcp:
                command_string = pack('<24sbb', str(user_id).encode(), temp_id, 1)
            else:
                command_string = pack('<Ib', int(user_id), temp_id)

            # Cancel any previous capture
            await asyncio.to_thread(self.zk.cancel_capture)

            # Send enrollment command
            cmd_response = await asyncio.to_thread(
                self.zk._ZK__send_command,
                command,
                command_string
            )

            if not cmd_response.get('status'):
                await self._emit_progress(
                    EnrollmentEvent.FAILED,
                    0,
                    max_attempts,
                    f"Failed to start enrollment for user #{uid} [{temp_id}]",
                    progress_callback
                )
                return False

            # Set socket timeout
            original_timeout = self.zk._ZK__sock.gettimeout()
            self.zk._ZK__sock.settimeout(timeout)

            # Process enrollment attempts
            result = await self._process_enrollment_attempts(
                max_attempts,
                progress_callback
            )

            # Restore original timeout
            self.zk._ZK__sock.settimeout(original_timeout)

            # Cleanup
            await asyncio.to_thread(self.zk.reg_event, 0)
            await asyncio.to_thread(self.zk.cancel_capture)
            await asyncio.to_thread(self.zk.verify_user)

            if result:
                await self._emit_progress(
                    EnrollmentEvent.COMPLETED,
                    max_attempts,
                    max_attempts,
                    "Enrollment completed successfully",
                    progress_callback
                )

            return result

        except Exception as e:
            await self._emit_progress(
                EnrollmentEvent.FAILED,
                0,
                max_attempts,
                f"Enrollment error: {str(e)}",
                progress_callback,
                {'error': str(e)}
            )
            return False

    async def _process_enrollment_attempts(
            self,
            max_attempts: int,
            progress_callback: Optional[Callable[[EnrollmentProgress], Awaitable[None]]]
    ) -> bool:
        """Process the enrollment attempts with progress tracking"""

        attempts_remaining = max_attempts
        current_attempt = 1

        while attempts_remaining > 0:
            if self._cancel_requested:
                await self._emit_progress(
                    EnrollmentEvent.CANCELLED,
                    current_attempt,
                    max_attempts,
                    "Enrollment cancelled by user",
                    progress_callback
                )
                return False

            await self._emit_progress(
                EnrollmentEvent.WAITING_FINGER,
                current_attempt,
                max_attempts,
                f"Place finger on scanner (attempt {current_attempt}/{max_attempts})",
                progress_callback
            )

            # Wait for first event (finger detection)
            try:
                data_recv = await asyncio.to_thread(self.zk._ZK__sock.recv, 1032)
                await asyncio.to_thread(self.zk._ZK__ack_ok)

                if self.zk.verbose:
                    print(codecs.encode(data_recv, 'hex'))

                # Parse response
                res = self._parse_response(data_recv)

                print("Received response code:", res)


                if res == 4:
                    await self._emit_progress(
                        EnrollmentEvent.CANCELLED,
                        current_attempt,
                        max_attempts,
                        "Enrollment cancelled by device",
                        progress_callback
                    )
                    break
                elif res == 0:
                    # Successful enrollment
                    await self._emit_progress(
                        EnrollmentEvent.COMPLETED,
                        current_attempt,
                        max_attempts,
                        "Enrollment completed successfully",
                        progress_callback
                    )
                    return True
                elif res == 6:
                    await self._emit_progress(
                        EnrollmentEvent.TIMEOUT,
                        current_attempt,
                        max_attempts,
                        "Timeout or registration failed",
                        progress_callback
                    )
                    break

                await self._emit_progress(
                    EnrollmentEvent.FINGER_DETECTED,
                    current_attempt,
                    max_attempts,
                    "Finger detected, processing...",
                    progress_callback
                )

                # Wait for second event (finger processing)
                data_recv = await asyncio.to_thread(self.zk._ZK__sock.recv, 1032)
                await asyncio.to_thread(self.zk._ZK__ack_ok)

                if self.zk.verbose:
                    print(codecs.encode(data_recv, 'hex'))

                res = self._parse_response(data_recv)

                print("Received response code after processing:", res)

                if res == 4:
                    await self._emit_progress(
                        EnrollmentEvent.CANCELLED,
                        current_attempt,
                        max_attempts,
                        "Enrollment cancelled by device",
                        progress_callback
                    )
                    break
                elif res == 6:
                    await self._emit_progress(
                        EnrollmentEvent.TIMEOUT,
                        current_attempt,
                        max_attempts,
                        "Timeout or registration failed",
                        progress_callback
                    )
                    break
                else:   # Continue
                    await self._emit_progress(
                        EnrollmentEvent.FINGER_PROCESSED,
                        current_attempt,
                        max_attempts,
                        f"Finger scan {current_attempt} processed successfully",
                        progress_callback
                    )
                    attempts_remaining -= 1
                    current_attempt += 1

                    await self._emit_progress(
                        EnrollmentEvent.ATTEMPT_COMPLETED,
                        current_attempt - 1,
                        max_attempts,
                        f"Completed {current_attempt - 1} of {max_attempts} scans",
                        progress_callback
                    )

            except asyncio.TimeoutError:
                await self._emit_progress(
                    EnrollmentEvent.TIMEOUT,
                    current_attempt,
                    max_attempts,
                    "Socket timeout waiting for device response",
                    progress_callback
                )
                break

        # Check final result
        if attempts_remaining == 0:
            data_recv = await asyncio.to_thread(self.zk._ZK__sock.recv, 1032)
            await asyncio.to_thread(self.zk._ZK__ack_ok)

            if self.zk.verbose:
                print(codecs.encode(data_recv, 'hex'))

            res = self._parse_response(data_recv)

            print("Received final response code:", res)

            if res == 5:
                await self._emit_progress(
                    EnrollmentEvent.DUPLICATE_FINGER,
                    max_attempts,
                    max_attempts,
                    "Duplicate fingerprint detected",
                    progress_callback
                )
                return False
            elif res == 6 or res == 4:
                await self._emit_progress(
                    EnrollmentEvent.TIMEOUT,
                    max_attempts,
                    max_attempts,
                    "Timeout during final verification",
                    progress_callback
                )
                return False
            elif res == 0:
                size = unpack("H", data_recv.ljust(16, b"\x00")[10:12])[0]
                pos = unpack("H", data_recv.ljust(16, b"\x00")[12:14])[0]

                await self._emit_progress(
                    EnrollmentEvent.COMPLETED,
                    max_attempts,
                    max_attempts,
                    f"Enrollment successful (size: {size}, pos: {pos})",
                    progress_callback,
                    {'size': size, 'position': pos}
                )
                return True

        return False

    def _parse_response(self, data_recv: bytes) -> int:
        """Parse device response code"""
        if self.zk.tcp:
            if len(data_recv) > 16:
                return unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0]
        else:
            if len(data_recv) > 8:
                return unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0]
        return -1

    async def _emit_progress(
            self,
            event: EnrollmentEvent,
            attempt: int,
            total_attempts: int,
            message: str,
            callback: Optional[Callable[[EnrollmentProgress], Awaitable[None]]],
            data: dict = None
    ):
        """Emit progress event to callback if provided"""
        if callback:
            progress = EnrollmentProgress(event, attempt, total_attempts, message, data)
            await callback(progress)

    def cancel_enrollment(self):
        """Request cancellation of ongoing enrollment"""
        self._cancel_requested = True


# Example usage
async def enrollment_progress_handler(progress: EnrollmentProgress):
    """Example callback handler for enrollment progress"""
    print(f"[{progress.event.value}] Attempt {progress.attempt}/{progress.total_attempts}: {progress.message}")

    # Here you could push to websocket, database, etc.
    # await websocket.send_json(progress.to_dict())
    # await redis.publish('enrollment_progress', json.dumps(progress.to_dict()))



async def main():
    """Example usage"""

    # Connect to device
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=5)
    conn = await asyncio.to_thread(zk.connect)

    if conn:
        print("Connected to device")

        users = await asyncio.to_thread(zk.get_users)

        for u in users:
            print(f"User: {u.user_id} (UID: {u.uid})")

        user = next((u for u in users if u.user_id == USER_ID ), None)
        if user:
            print(f"User found: {user.user_id} (UID: {user.uid})")
        else:
            print(f"User not found: {user.user_id} (UID: {user.uid})")
        print(user)
        # return

        # Create async enrollment instance
        enrollment = AsyncBiometricEnrollment(zk)

        # Enroll user with progress callback
        success = await enrollment.enroll_user_async(
            uid=user.uid if user else 0,
            temp_id=FINGER_ID,
            user_id=USER_ID,
            progress_callback=enrollment_progress_handler,
            timeout=60,
            max_attempts=3
        )

        if success:
            print("Enrollment completed successfully!")
        else:
            print("Enrollment failed!")

        # Disconnect
        await asyncio.to_thread(zk.disconnect)


# For WebSocket integration example
async def websocket_progress_handler(websocket, progress: EnrollmentProgress):
    """Example WebSocket callback handler"""
    import json
    await websocket.send(json.dumps(progress.to_dict()))


# Run the example
if __name__ == "__main__":
    asyncio.run(main())