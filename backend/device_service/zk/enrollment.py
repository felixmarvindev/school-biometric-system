"""
Async fingerprint enrollment logic aligned with verify_test_2.

This module provides AsyncBiometricEnrollment - the verified enrollment flow
that properly emits all progress events (STARTED, WAITING_FINGER, FINGER_DETECTED,
FINGER_PROCESSED, ATTEMPT_COMPLETED, COMPLETED, etc.) for UI broadcasting.
"""

import asyncio
from enum import Enum
from typing import Callable, Optional, Awaitable
from struct import pack, unpack

# Use pyzk (system package), not device_service zk
from zk import const


class EnrollmentEvent(str, Enum):
    """Enumeration of enrollment progress events - matches verify_test_2."""

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
    """Data class for enrollment progress information."""

    def __init__(
        self,
        event: EnrollmentEvent,
        attempt: int,
        total_attempts: int,
        message: str = "",
        data: Optional[dict] = None,
    ):
        self.event = event
        self.attempt = attempt
        self.total_attempts = total_attempts
        self.message = message
        self.data = data or {}
        self.timestamp = asyncio.get_event_loop().time()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/broadcasting."""
        return {
            "event": self.event.value,
            "attempt": self.attempt,
            "total_attempts": self.total_attempts,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }


class AsyncBiometricEnrollment:
    """Async wrapper for ZK device enrollment with callback support - aligned with verify_test_2."""

    def __init__(self, zk_instance):
        """
        Initialize with a ZK instance (pyzk connection).

        :param zk_instance: Connected ZK object from pyzk
        """
        self.zk = zk_instance
        self._cancel_requested = False

    async def enroll_user_async(
        self,
        uid: int = 0,
        temp_id: int = 0,
        user_id: str = "",
        progress_callback: Optional[Callable[[EnrollmentProgress], Awaitable[None]]] = None,
        timeout: int = 60,
        max_attempts: int = 3,
    ) -> bool:
        """
        Asynchronously enroll a user with progress callbacks.

        :param uid: User UID
        :param temp_id: Template ID (finger index 0-9)
        :param user_id: User ID string
        :param progress_callback: Async callback for progress updates (broadcasts to UI)
        :param timeout: Timeout in seconds for enrollment
        :param max_attempts: Maximum finger scan attempts (default 3)
        :return: True if enrollment successful, False otherwise
        """
        self._cancel_requested = False

        await self._emit_progress(
            EnrollmentEvent.STARTED,
            0,
            max_attempts,
            f"Starting enrollment for user {user_id or uid}, template {temp_id}",
            progress_callback,
        )

        try:
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
                        progress_callback,
                    )
                    return False

            command = const.CMD_STARTENROLL
            if self.zk.tcp:
                command_string = pack("<24sbb", str(user_id).encode(), temp_id, 1)
            else:
                command_string = pack("<Ib", int(user_id), temp_id)

            await asyncio.to_thread(self.zk.cancel_capture)

            cmd_response = await asyncio.to_thread(
                self.zk._ZK__send_command,
                command,
                command_string,
            )

            if not cmd_response.get("status"):
                await self._emit_progress(
                    EnrollmentEvent.FAILED,
                    0,
                    max_attempts,
                    f"Failed to start enrollment for user #{uid} [{temp_id}]",
                    progress_callback,
                )
                return False

            original_timeout = self.zk._ZK__sock.gettimeout()
            self.zk._ZK__sock.settimeout(timeout)

            result = await self._process_enrollment_attempts(
                max_attempts,
                progress_callback,
            )

            self.zk._ZK__sock.settimeout(original_timeout)

            await asyncio.to_thread(self.zk.reg_event, 0)
            await asyncio.to_thread(self.zk.cancel_capture)
            await asyncio.to_thread(self.zk.verify_user)

            if result:
                await self._emit_progress(
                    EnrollmentEvent.COMPLETED,
                    max_attempts,
                    max_attempts,
                    "Enrollment completed successfully",
                    progress_callback,
                )

            return result

        except Exception as e:
            await self._emit_progress(
                EnrollmentEvent.FAILED,
                0,
                max_attempts,
                f"Enrollment error: {str(e)}",
                progress_callback,
                {"error": str(e)},
            )
            return False

    async def _process_enrollment_attempts(
        self,
        max_attempts: int,
        progress_callback: Optional[Callable[[EnrollmentProgress], Awaitable[None]]],
    ) -> bool:
        """Process enrollment attempts - matches verify_test_2 flow exactly."""
        attempts_remaining = max_attempts
        current_attempt = 1

        while attempts_remaining > 0:
            if self._cancel_requested:
                await self._emit_progress(
                    EnrollmentEvent.CANCELLED,
                    current_attempt,
                    max_attempts,
                    "Enrollment cancelled by user",
                    progress_callback,
                )
                return False

            await self._emit_progress(
                EnrollmentEvent.WAITING_FINGER,
                current_attempt,
                max_attempts,
                f"Place finger on scanner (attempt {current_attempt}/{max_attempts})",
                progress_callback,
            )

            try:
                data_recv = await asyncio.to_thread(self.zk._ZK__sock.recv, 1032)
                await asyncio.to_thread(self.zk._ZK__ack_ok)

                res = self._parse_response(data_recv)

                if res == 4:
                    await self._emit_progress(
                        EnrollmentEvent.CANCELLED,
                        current_attempt,
                        max_attempts,
                        "Enrollment cancelled by device",
                        progress_callback,
                    )
                    break
                elif res == 0:
                    await self._emit_progress(
                        EnrollmentEvent.COMPLETED,
                        current_attempt,
                        max_attempts,
                        "Enrollment completed successfully",
                        progress_callback,
                    )
                    return True
                elif res == 6:
                    await self._emit_progress(
                        EnrollmentEvent.TIMEOUT,
                        current_attempt,
                        max_attempts,
                        "Timeout or registration failed",
                        progress_callback,
                    )
                    break

                await self._emit_progress(
                    EnrollmentEvent.FINGER_DETECTED,
                    current_attempt,
                    max_attempts,
                    "Finger detected, processing...",
                    progress_callback,
                )

                data_recv = await asyncio.to_thread(self.zk._ZK__sock.recv, 1032)
                await asyncio.to_thread(self.zk._ZK__ack_ok)

                res = self._parse_response(data_recv)

                if res == 4:
                    await self._emit_progress(
                        EnrollmentEvent.CANCELLED,
                        current_attempt,
                        max_attempts,
                        "Enrollment cancelled by device",
                        progress_callback,
                    )
                    break
                elif res == 6:
                    await self._emit_progress(
                        EnrollmentEvent.TIMEOUT,
                        current_attempt,
                        max_attempts,
                        "Timeout or registration failed",
                        progress_callback,
                    )
                    break
                else:
                    await self._emit_progress(
                        EnrollmentEvent.FINGER_PROCESSED,
                        current_attempt,
                        max_attempts,
                        f"Finger scan {current_attempt} processed successfully",
                        progress_callback,
                    )
                    attempts_remaining -= 1
                    current_attempt += 1

                    await self._emit_progress(
                        EnrollmentEvent.ATTEMPT_COMPLETED,
                        current_attempt - 1,
                        max_attempts,
                        f"Completed {current_attempt - 1} of {max_attempts} scans",
                        progress_callback,
                    )

            except asyncio.TimeoutError:
                await self._emit_progress(
                    EnrollmentEvent.TIMEOUT,
                    current_attempt,
                    max_attempts,
                    "Socket timeout waiting for device response",
                    progress_callback,
                )
                break

        if attempts_remaining == 0:
            data_recv = await asyncio.to_thread(self.zk._ZK__sock.recv, 1032)
            await asyncio.to_thread(self.zk._ZK__ack_ok)

            res = self._parse_response(data_recv)

            if res == 5:
                await self._emit_progress(
                    EnrollmentEvent.DUPLICATE_FINGER,
                    max_attempts,
                    max_attempts,
                    "Duplicate fingerprint detected",
                    progress_callback,
                )
                return False
            elif res in (6, 4):
                await self._emit_progress(
                    EnrollmentEvent.TIMEOUT,
                    max_attempts,
                    max_attempts,
                    "Timeout during final verification",
                    progress_callback,
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
                    {"size": size, "position": pos},
                )
                return True

        return False

    def _parse_response(self, data_recv: bytes) -> int:
        """Parse device response code - matches verify_test_2."""
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
        data: Optional[dict] = None,
    ) -> None:
        """Emit progress event to callback if provided."""
        if callback:
            progress = EnrollmentProgress(event, attempt, total_attempts, message, data)
            await callback(progress)

    def cancel_enrollment(self) -> None:
        """Request cancellation of ongoing enrollment."""
        self._cancel_requested = True
