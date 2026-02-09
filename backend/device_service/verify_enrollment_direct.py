#!/usr/bin/env python3
"""
Verify ZKTeco enrollment event registration flow (enroll_user logic).

This script verifies that the realtime fingerprint enrollment/capture flow works correctly
by executing the exact steps from pyzk's enroll_user() function. It does NOT stream
fingerprint image/template - it tells the device to start enrollment and listens for
enrollment events over the socket (recv()), interpreting status codes until success/fail.

Uses async patterns and callbacks for application-ready verification:
- All blocking pyzk/socket calls run in asyncio.to_thread
- Callback(event_type, progress, status, message) for real-time updates (WebSocket, UI)

Uses pyzk library directly - NO imports from device_service.
 
Usage (from project root, with venv activated):
    python backend/device_service/verify_enrollment_direct.py

Device config (edit constants below):
    IP: 192.168.0.121, Port: 4370, User ID: 3, Finger: 0 (right thumb)
"""

import sys
from pathlib import Path

# Ensure we import pyzk's zk, not local device_service/zk/
_script_dir = str(Path(__file__).resolve().parent)
if _script_dir in sys.path:
    sys.path.remove(_script_dir)

import asyncio
import logging
from struct import pack, unpack
from socket import timeout as SocketTimeout
from typing import Callable, Awaitable

from zk import ZK

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# --- Device config (edit these) ---
DEVICE_IP = "192.168.0.121"
DEVICE_PORT = 4370
DEVICE_PASSWORD = None
UID = 3
TEMP_ID = 0  # 0 = right thumb
USER_ID_INPUT = ""  # Empty = resolve from get_users() by uid
TIMEOUT = 60
CONNECT_TIMEOUT = 10

# --- Response codes ---
RES_TIMEOUT_FAIL = (6, 4)
RES_PRESS_OK = 0x64
RES_DUPLICATE = 5
RES_SUCCESS = 0
# --- ZKTeco protocol constants ---
CMD_STARTENROLL = 61
CMD_REG_EVENT = 500
EF_ENROLLFINGER = 8


# --- Callback type: (event_type, progress, status, message) -> None or Awaitable ---
EnrollmentCallback = Callable[[str, int, str, str], None | Awaitable[None]]


async def run_in_thread(func, *args, **kwargs):
    """Run blocking pyzk calls in thread pool."""
    return await asyncio.to_thread(func, *args, **kwargs)


async def _invoke_callback(
    callback: EnrollmentCallback | None,
    event_type: str,
    progress: int,
    status: str,
    message: str,
) -> None:
    """Invoke callback (supports sync and async callbacks)."""
    if callback:
        result = callback(event_type, progress, status, message)
        if asyncio.iscoroutine(result):
            await result


def _parse_res(conn: ZK, data: bytes) -> int:
    """Extract 2-byte result/status from enrollment event packet."""
    if conn.tcp:
        return unpack("H", data.ljust(24, b"\x00")[16:18])[0] if len(data) > 16 else -1
    return unpack("H", data.ljust(16, b"\x00")[8:10])[0] if len(data) > 8 else -1


async def _recv_event(conn: ZK) -> tuple[bytes, int]:
    """Receive enrollment event packet, ack, and parse res. Returns (data, res)."""
    data = await run_in_thread(conn._ZK__sock.recv, 1032)
    await run_in_thread(conn._ZK__ack_ok)
    return data, _parse_res(conn, data)


def _is_first_event_stop(conn: ZK, res: int) -> bool:
    """True if first reg event indicates stop (timeout/cancel)."""
    if conn.tcp:
        return res in (0, 6, 4)
    return res in RES_TIMEOUT_FAIL


def _is_timeout_or_fail(res: int) -> bool:
    """True if res indicates timeout or failure."""
    return res in RES_TIMEOUT_FAIL


def _extract_size_pos(data: bytes) -> tuple[int, int]:
    """Extract size and pos from success packet."""
    buf = data.ljust(16, b"\x00")
    return unpack("H", buf[10:12])[0], unpack("H", buf[12:14])[0]


async def connect_device() -> ZK | None:
    """Connect to ZKTeco device. Returns ZK connection or None."""
    zk = ZK(
        DEVICE_IP,
        port=DEVICE_PORT,
        timeout=CONNECT_TIMEOUT,
        password=int(DEVICE_PASSWORD) if DEVICE_PASSWORD else 0,
        ommit_ping=False,
    )
    try:
        conn = await run_in_thread(zk.connect)
        if conn:
            log.info("Connected to %s:%s", DEVICE_IP, DEVICE_PORT)
            return conn
    except Exception as e:
        log.error("Connection failed: %s", e)
    return None


async def verify_enroll_user(
    conn: ZK,
    callback: EnrollmentCallback | None = None,
) -> bool:
    """
    Execute enroll_user() flow step-by-step (async, with callbacks).

    Mirrors pyzk's enroll_user() logic exactly:
    1) Resolve target user
    2) Build start enroll command payload (TCP vs non-TCP)
    3) Clear any previous capture state
    4) Send start enroll to device
    5) Switch socket to 60s timeout
    6) Realtime event loop for 3 enrollment presses (two receives per attempt)
    7) After 3 successful presses, read final enrollment result
    8) Cleanup / restore device state

    Callback is invoked with (event_type, progress, status, message) for real-time
    updates - suitable for WebSocket broadcasting or UI updates in the application.

    Args:
        conn: ZK connection
        callback: Optional async or sync callback(event_type, progress, status, message)

    Returns:
        True if enrollment completed successfully, False otherwise.
    """
    from zk import const
    from zk.exception import ZKErrorResponse

    uid = UID
    temp_id = TEMP_ID
    user_id = USER_ID_INPUT

    log.info("=" * 50)
    log.info("STEP 1: Resolve target user (uid=%s, temp_id=%s, user_id=%r)", uid, temp_id, user_id)

    # 1) Resolve the target user
    if not user_id:
        users = await run_in_thread(conn.get_users)
        users = [x for x in users if x.uid == uid]
        if len(users) >= 1:
            user_id = users[0].user_id
            log.info("  Resolved user_id from get_users: %r", user_id)
        else:
            log.error("  FAIL: User with uid=%s not found on device", uid)
            await _invoke_callback(callback, "error", 0, "error", f"User uid={uid} not found")
            return False
    else:
        log.info("  Using provided user_id: %r", user_id)

    log.info("=" * 50)
    log.info("STEP 2: Build 'start enroll' command payload (TCP=%s)", conn.tcp)

    command = const.CMD_STARTENROLL
    if conn.tcp:
        command_string = pack("<24sbb", str(user_id).encode()[:24].ljust(24, b"\x00"), temp_id, 1)
        log.info("  TCP: pack('<24sbb', user_id=%r, temp_id=%s, 1)", user_id, temp_id)
    else:
        command_string = pack("<Ib", int(user_id) if str(user_id).isdigit() else 0, temp_id)
        log.info("  non-TCP: pack('<Ib', user_id=%s, temp_id=%s)", user_id, temp_id)

    log.info("=" * 50)
    log.info("STEP 3: Clear any previous capture state (cancel_capture)")

    await run_in_thread(conn.cancel_capture)
    log.info("  cancel_capture() done")

    log.info("=" * 50)
    log.info("STEP 4: Send 'start enroll' to device")

    try:
        cmd_response = await run_in_thread(conn._ZK__send_command, command, command_string)
        if not cmd_response.get("status"):
            raise ZKErrorResponse(f"Cant Enroll user #{uid} [{temp_id}]")
        log.info("  Device accepted start enroll command")
    except ZKErrorResponse as e:
        log.error("  FAIL: %s", e)
        await _invoke_callback(callback, "error", 0, "error", str(e))
        return False

    await _invoke_callback(
        callback, "progress", 0, "ready",
        "Enrollment started. Place your finger on the scanner.",
    )

    log.info("=" * 50)
    log.info("STEP 5: Switch socket to 60s timeout for interactive scanning")

    original_timeout = conn._ZK__timeout
    await run_in_thread(conn._ZK__sock.settimeout, 60)
    log.info("  Original timeout=%s, new timeout=60", original_timeout)

    log.info("=" * 50)
    log.info("STEP 6: Realtime event loop for 3 enrollment presses")

    attempts = 3
    max_attempts = 3
    done = False

    while attempts:
        log.info("  --- Attempt %s ---", max_attempts - attempts + 1)

        # (a) First reg event
        log.info("  (a) Waiting for first reg event...")
        _, res = await _recv_event(conn)
        log.info("  First event res=%s", res)

        if _is_first_event_stop(conn, res):
            msg = "Enrollment timeout" if res == 6 else "Enrollment cancelled by device"
            await _invoke_callback(callback, "error", 0, "error", msg)
            break

        await _invoke_callback(
            callback, "progress", 33, "placing",
            "Finger detected. Keep your finger steady...",
        )

        # log the res
        log.info("  First event res=%s", res)
        attempts -= 1
        await _invoke_callback(
            callback, "progress", 66, "processing",
            f"Press {max_attempts - attempts}/{max_attempts} captured. Place finger again.",
        )

        # if res == RES_PRESS_OK:
        #     attempts -= 1
        #     await _invoke_callback(
        #         callback, "progress", 66, "processing",
        #         f"Press {max_attempts - attempts}/{max_attempts} captured. Place finger again.",
        #     )
        #     continue

        # (b) Second reg event
        # log.info("  (b) Waiting for second reg event...")
        # _, res = await _recv_event(conn)
        # log.info("  Second event res=%s", res)
        #
        # if _is_timeout_or_fail(res):
        #     await _invoke_callback(callback, "error", 0, "error", "Enrollment timeout")
        #     break
        # if res == RES_PRESS_OK:
        #     attempts -= 1
        #     await _invoke_callback(
        #         callback, "progress", 66, "processing",
        #         f"Press {max_attempts - attempts}/{max_attempts} captured. Place finger again.",
        #     )
        #     continue

    log.info("=" * 50)
    log.info("STEP 7: After loop, read final enrollment result (attempts=%s)", attempts)

    if attempts == 0:
        log.info("  Waiting for final packet...")
        data_recv, res = await _recv_event(conn)
        log.info("  Final res=%s", res)

        if res == RES_DUPLICATE:
            await _invoke_callback(callback, "error", 0, "error", "This fingerprint is already enrolled")
        elif _is_timeout_or_fail(res):
            await _invoke_callback(callback, "error", 0, "error", "Enrollment timeout")
        elif res == RES_SUCCESS:
            size, pos = _extract_size_pos(data_recv)
            log.info("  SUCCESS: size=%s, pos=%s", size, pos)
            done = True
            await _invoke_callback(
                callback, "complete", 100, "complete",
                f"Enrollment completed (size={size}, pos={pos})",
            )

    log.info("=" * 50)
    log.info("STEP 8: Cleanup / restore device state")

    await run_in_thread(conn._ZK__sock.settimeout, original_timeout)
    log.info("  Restored socket timeout to %s", original_timeout)

    await run_in_thread(conn.reg_event, 0)
    log.info("  reg_event(0) - unregistered events")

    await run_in_thread(conn.cancel_capture)
    log.info("  cancel_capture() - stopped capture mode")

    await run_in_thread(conn.verify_user)
    log.info("  verify_user() - refreshed verify mode")

    log.info("  done=%s", done)
    return done


def log_callback(event_type: str, progress: int, status: str, message: str) -> None:
    """Example callback: log enrollment updates (simulates WebSocket/UI payload)."""
    log.info(">>> [%s] progress=%s%% | status=%s | %s", event_type, progress, status, message)


async def main() -> None:
    """Run enrollment flow verification with async and callbacks."""
    print("=" * 60)
    print("ZKTeco Verify Enrollment Direct (async + callbacks)")
    print("=" * 60)
    print(f"Device: {DEVICE_IP}:{DEVICE_PORT} | UID: {UID} | Temp: {TEMP_ID}")
    print(f"User ID input: {USER_ID_INPUT or '(resolve from get_users)'}")
    print("Actions: place finger on device when prompted (3 presses)")
    print("Callback: log_callback (ready for WebSocket in application)")
    print("=" * 60)

    conn = await connect_device()
    if not conn:
        print("FAILED: Could not connect.")
        return

    try:
        done = await verify_enroll_user(conn, callback=log_callback)
        print("-" * 60)
        if done:
            print("VERIFY PASSED: Enrollment completed successfully.")
        else:
            print("VERIFY FAILED: Enrollment did not complete.")
    except SocketTimeout:
        print("FAILED: Socket timeout waiting for enrollment events.")
    except Exception as e:
        log.error("Error: %s", e, exc_info=True)
        print(f"FAILED: {e}")
    finally:
        try:
            await run_in_thread(conn.disconnect)
        except Exception:
            pass
        print("\nDisconnected from device.")


async def main2():
    """ Capture live events without async/await, for debugging. """
    conn = await connect_device()
    if not conn:
        print("FAILED: Could not connect.")
        return

    print("Waiting for events...")
    conn.live_capture(new_timeout=CONNECT_TIMEOUT)

if __name__ == "__main__":
    asyncio.run(main2())
    # main2()