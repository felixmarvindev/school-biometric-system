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
import logging
import time
from struct import pack, unpack, error as struct_error
from socket import timeout as SocketTimeout

# Only external dependency: pyzk (pip install pyzk)
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
USER_ID = '3'
FINGER_ID = 1  # 0 = right thumb
TIMEOUT = 60   # seconds to wait for finger
CONNECT_TIMEOUT = 10

# If True: delete existing fingerprint and re-enroll. If False: fail when finger already enrolled.
FORCE_REENROLL = True


# --- ZKTeco protocol constants ---
CMD_STARTENROLL = 61
CMD_REG_EVENT = 500
EF_ENROLLFINGER = 8


def log_update(event_type: str, progress: int, status: str, message: str) -> None:
    """Log enrollment update (simulates WebSocket payload)."""
    log.info(">>> [%s] progress=%s%% | status=%s | %s", event_type, progress, status, message)


async def run_in_thread(func, *args, **kwargs):
    """Run blocking pyzk calls in thread pool."""
    return await asyncio.to_thread(func, *args, **kwargs)


async def connect_device() -> ZK | None:
    """Connect to ZKTeco device. Returns ZK connection or None."""
    zk = ZK(
        DEVICE_IP,
        port=DEVICE_PORT,
        timeout=CONNECT_TIMEOUT,
        password=int(DEVICE_PASSWORD) if DEVICE_PASSWORD else 0,
        ommit_ping=False
    )
    try:
        conn = await run_in_thread(zk.connect)
        if conn:
            log.info("Connected to %s:%s", DEVICE_IP, DEVICE_PORT)
            return conn
    except Exception as e:
        log.error("Connection failed: %s", e)
    return None

async def get_templates(conn) -> list:
    """Get list of enrolled fingerprint templates on device. Returns list of UserTemplate objects."""
    try:
        templates = await run_in_thread(conn.get_templates)
        return templates or []
    except Exception as e:
        log.warning("get_templates failed: %s", e)
        return []

async def get_users(conn: ZK) -> list:
    """Get list of users on device. Returns User objects with uid, user_id, name."""
    try:
        users = await run_in_thread(conn.get_users)
        return users or []
    except Exception as e:
        log.warning("get_users failed: %s", e)
        return []


async def finger_already_enrolled(conn: ZK,user_id_str: str, finger_id: int) -> bool:
    """Check if user already has fingerprint for given finger_id on device."""
    try:
        finger = await run_in_thread(
            conn.get_user_template,
            uid=None,
            temp_id=finger_id,
            user_id=user_id_str,
        )

        print(f"finger: {finger}")
        return finger is not None and bool(getattr(finger, "template", None))
    except Exception as e:
        log.debug("finger_already_enrolled check: %s", e)
        return False


async def ensure_user(conn: ZK) -> tuple[str, int] | None:
    """
    Register user on device or return existing user info for enrollment.
    Returns (user_id_str, device_uid) or None on failure.
    """
    users = await get_users(conn)
    if users:
        log.info("Existing users on device: %s", [(u.uid, u.user_id, u.name) for u in users[:10]])
        # Use existing user with uid=USER_ID or user_id=str(USER_ID)
        for u in users:
            if u.user_id == str(USER_ID):
                log.info("Using existing user: uid=%s user_id=%s", u.uid, u.user_id)
                return (u.user_id, u.uid)
        # Fallback: use first user for testing
        u = users[0]
        log.info("Using first existing user: uid=%s user_id=%s (change USER_ID to match)", u.uid, u.user_id)
        return (u.user_id, u.uid)

    try:
        await run_in_thread(
            conn.set_user,
            uid=USER_ID,
            name=f"User {USER_ID}",
            privilege=0,
            user_id=str(USER_ID),
        )
        log.info("User %s registered on device", USER_ID)
        return (str(USER_ID), USER_ID)
    except Exception as e:
        log.warning("set_user failed: %s", e)
        return None


async def start_enrollment(conn: ZK, user_id_str: str) -> bool:
    """Send CMD_STARTENROLL to device. Returns True if accepted."""
    try:
        await run_in_thread(conn.cancel_capture)

        command = CMD_STARTENROLL

        if conn.tcp:
            command_string = pack(
                "<24sbb",
                user_id_str.encode("utf-8")[:24].ljust(24, b"\x00"),
                FINGER_ID,
                1,
            )
        else:
            command_string = pack("<Ib", int(user_id_str) if user_id_str.isdigit() else 0, FINGER_ID)

        cmd_response = await run_in_thread(conn._ZK__send_command, command, command_string)

        if cmd_response and cmd_response.get("status"):
            log.info("Enrollment started: user_id=%s, finger_id=%s", user_id_str, FINGER_ID)
            return True

        log.warning("Enrollment start failed: response=%s", cmd_response)
        return False

    except Exception as e:
        log.error("start_enrollment error: %s", e, exc_info=True)
        return False


async def poll_enrollment_events(
    conn: ZK,
    callback=None,
    timeout: int = TIMEOUT,
    max_attempts: int = 3,
) -> dict:
    """
    Poll device socket for enrollment events. Calls callback with updates.
    Returns dict with success, status, message.
    """
    original_timeout = conn._ZK__timeout
    conn._ZK__sock.settimeout(timeout)

    attempts = max_attempts
    progress = 0
    status = "placing"
    message = "Place your finger on the scanner"

    if callback:
        await callback("progress", 0, "ready", "Enrollment started. Place your finger on the scanner.")

    while attempts > 0:
        try:
            wait_start = time.monotonic()
            log.debug("Waiting for register event (attempt %s)...", attempts)
            data_recv = await run_in_thread(conn._ZK__sock.recv, 1032)
            await run_in_thread(conn._ZK__ack_ok)

            if conn.tcp:
                res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0] if len(data_recv) > 16 else -1
            else:
                res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0] if len(data_recv) > 8 else -1

            print("Result code on first event:", res)

            # Early termination: res 0,4 = cancel OR timeout (same code; use elapsed time to tell)
            # res 6 = timeout. For res 0,4: long wait (~timeout) = timeout, short wait = cancel
            if res == 0 or res == 6 or res == 4:
                elapsed = time.monotonic() - wait_start
                log.debug("Early termination: res=%s, elapsed=%.1fs", res, elapsed)
                if res == 6:
                    cancel_msg = "Enrollment timeout"
                elif elapsed >= timeout - 5:  # Close to socket timeout = no finger placed
                    cancel_msg = "Enrollment timeout"
                else:
                    cancel_msg = "Enrollment cancelled by device"
                if callback:
                    await callback("error", 0, "error", cancel_msg)
                try:
                    conn._ZK__sock.settimeout(original_timeout)
                    await run_in_thread(conn.reg_event, 0)
                    await run_in_thread(conn.cancel_capture)
                except Exception as e:
                    log.warning("Cleanup: %s", e)
                return {"success": False, "status": "error", "message": cancel_msg}

            # Finger placed (33%)
            if callback:
                await callback("progress", 33, "placing", "Finger detected. Keep your finger steady...")

            log.debug("Waiting for second register event...")
            data_recv = await run_in_thread(conn._ZK__sock.recv, 1032)
            await run_in_thread(conn._ZK__ack_ok)

            if conn.tcp:
                res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0] if len(data_recv) > 16 else -1
            else:
                res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0] if len(data_recv) > 8 else -1

            print("Result code on second event:", res)

            if res == 6 or res == 4:
                elapsed = time.monotonic() - wait_start
                log.debug("Second event termination: res=%s, elapsed=%.1fs", res, elapsed)
                if res == 6 or elapsed >= timeout - 5:
                    msg = "Enrollment timeout"
                else:
                    msg = "Enrollment cancelled by device"
                if callback:
                    await callback("error", 0, "error", msg)
                try:
                    conn._ZK__sock.settimeout(original_timeout)
                    await run_in_thread(conn.reg_event, 0)
                    await run_in_thread(conn.cancel_capture)
                except Exception as e:
                    log.warning("Cleanup: %s", e)
                return {"success": False, "status": "error", "message": msg}
            elif res == 0x64:  # 100 - low quality, retry
                log.debug("Finger quality low, retrying...")
                attempts -= 1
                if callback:
                    await callback("progress", 66, "processing", f"Finger quality low. Attempt {max_attempts - attempts + 1}/{max_attempts}.")
                continue

            # Capturing (66%)
            if callback:
                await callback("progress", 66, "capturing", "Capturing fingerprint data...")

            # Final event: completion (res=0 success, res=5 duplicate, res=6/4 timeout)
            log.debug("Waiting for final event (completion)...")
            data_recv = await run_in_thread(conn._ZK__sock.recv, 1032)
            await run_in_thread(conn._ZK__ack_ok)

            if conn.tcp:
                res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0] if len(data_recv) > 16 else -1
            else:
                res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0] if len(data_recv) > 8 else -1

            print("Result code on final event:", res)

            # Success: res 0 = common. Many ZKTeco devices return 46,50,54,55 etc for success.
            # Known errors only: 4,6 = timeout, 5 = duplicate. Treat anything else as success.
            if res not in (4, 5, 6):
                try:
                    size = unpack("H", data_recv.ljust(16, b"\x00")[10:12])[0]
                    pos = unpack("H", data_recv.ljust(16, b"\x00")[12:14])[0]
                    msg = f"Enrollment completed (size={size}, pos={pos})"
                except (IndexError, struct_error):
                    msg = "Enrollment completed successfully"
                try:
                    conn._ZK__sock.settimeout(original_timeout)
                    await run_in_thread(conn.reg_event, 0)
                    await run_in_thread(conn.cancel_capture)
                except Exception as e:
                    log.warning("Cleanup after success: %s", e)
                if callback:
                    await callback("complete", 100, "complete", msg)
                return {"success": True, "status": "complete", "message": msg}

            if res == 5:
                msg = "This fingerprint is already enrolled"
                if callback:
                    await callback("error", 0, "error", msg)
                return {"success": False, "status": "error", "message": msg}
            elif res == 6 or res == 4:
                msg = "Enrollment timeout"
                if callback:
                    await callback("error", 0, "error", msg)
                return {"success": False, "status": "error", "message": msg}
            else:
                msg = f"Unexpected enrollment result: res={res}"
                if callback:
                    await callback("error", 0, "error", msg)
                return {"success": False, "status": "error", "message": msg}

        except SocketTimeout:
            log.warning("Timeout waiting for enrollment event")
            if callback:
                await callback("error", 0, "error", "Enrollment timeout. Please try again.")
            return {"success": False, "status": "error", "message": "Enrollment timeout"}
        except Exception as e:
            log.error("Error polling event: %s", e, exc_info=True)
            if callback:
                await callback("error", 0, "error", str(e))
            return {"success": False, "status": "error", "message": str(e)}

    # Final event (completion) when attempts exhausted
    if attempts == 0:
        try:
            log.debug("Waiting for final event...")
            data_recv = await run_in_thread(conn._ZK__sock.recv, 1032)
            await run_in_thread(conn._ZK__ack_ok)

            if conn.tcp:
                res = unpack("H", data_recv.ljust(24, b"\x00")[16:18])[0]
            else:
                res = unpack("H", data_recv.ljust(16, b"\x00")[8:10])[0]

            print("Result code on final event after attempts exhausted:", res)

            if res == 5:
                msg = "This fingerprint is already enrolled"
                if callback:
                    await callback("error", 0, "error", msg)
                return {"success": False, "status": "error", "message": msg}
            elif res == 6 or res == 4:
                msg = "Enrollment timeout"
                if callback:
                    await callback("error", 0, "error", msg)
                return {"success": False, "status": "error", "message": msg}
            elif res == 0:
                size = unpack("H", data_recv.ljust(16, b"\x00")[10:12])[0]
                pos = unpack("H", data_recv.ljust(16, b"\x00")[12:14])[0]
                msg = f"Enrollment completed (size={size}, pos={pos})"
                try:
                    conn._ZK__sock.settimeout(original_timeout)
                    await run_in_thread(conn.reg_event, 0)
                    await run_in_thread(conn.cancel_capture)
                except Exception as e:
                    log.warning("Cleanup after success: %s", e)
                if callback:
                    await callback("complete", 100, "complete", msg)
                return {"success": True, "status": "complete", "message": msg}
            else:
                msg = f"Unexpected result: res={res}"
                if callback:
                    await callback("error", 0, "error", msg)
                return {"success": False, "status": "error", "message": msg}

        except SocketTimeout:
            msg = "Timeout waiting for completion"
            if callback:
                await callback("error", 0, "error", msg)
            return {"success": False, "status": "error", "message": msg}
        except Exception as e:
            log.error("Error on final event: %s", e, exc_info=True)
            if callback:
                await callback("error", 0, "error", str(e))
            return {"success": False, "status": "error", "message": str(e)}

    # Cleanup after early break
    try:
        conn._ZK__sock.settimeout(original_timeout)
        await run_in_thread(conn.reg_event, 0)
        await run_in_thread(conn.cancel_capture)
    except Exception as e:
        log.warning("Cleanup: %s", e)

    return {"success": False, "status": "error", "message": "Enrollment failed"}


async def main() -> None:
    """Run enrollment test flow."""
    print("=" * 60)
    print("ZKTeco Enrollment Direct Test (standalone, no device_service)")
    print("=" * 60)
    print(f"Device: {DEVICE_IP}:{DEVICE_PORT} | User: {USER_ID} | Finger: {FINGER_ID}")
    print(f"Timeout: {TIMEOUT}s")
    print("Actions: place finger | cancel on device | wait for timeout")
    print("=" * 60)

    conn = await connect_device()
    if not conn:
        print("FAILED: Could not connect.")
        return

    try:
        user_info = await ensure_user(conn)
        if not user_info:
            print("FAILED: No user on device. Add user via device menu or fix set_user.")
            return

        user_id_str, device_uid = user_info

        print(f"user_id_str: {user_id_str}, device_uid: {device_uid}")

        finger_found = await finger_already_enrolled(conn, user_id_str, FINGER_ID)

        templates = await get_templates(conn)
        # Print in table format
        for t in templates[:10]:
            print(t)

        conn.read_sizes()
        print("=" * 60)
        print(conn.fingers)
        # return

        if finger_found :

            if FORCE_REENROLL:
                log.info("Finger %s already enrolled - deleting existing template (FORCE_REENROLL=True)", FINGER_ID)
                try:
                    # Use uid path: pyzk's user_id path has pack bug with str/bytes in Python 3
                    await run_in_thread(
                        conn.delete_user_template,
                        uid=device_uid,
                        temp_id=FINGER_ID,
                        user_id="",
                    )
                    log.info("Existing template deleted. Proceeding with enrollment.")
                except Exception as e:
                    print(f"FAILED: Could not delete existing template: {e}")
                    return
            else:
                print(
                    f"FAILED: Finger {FINGER_ID} already enrolled for user {user_id_str}. "
                    "Choose a different finger, or set FORCE_REENROLL=True to overwrite."
                )
                return

        # await run_in_thread(conn.enroll_user, uid= device_uid,
        #         temp_id = FINGER_ID,
        #         user_id = user_id_str)

        print("UId: ", device_uid)
        templates = await get_templates(conn)
        # Print in table format
        for t in templates[:10]:
            print(t)

        return

        await run_in_thread(conn.reg_event, EF_ENROLLFINGER)

        if not await start_enrollment(conn, user_id_str):
            print("FAILED: Could not start enrollment (e.g. error 2001 = user not found).")
            return

        async def on_update(event_type: str, progress: int, status: str, message: str) -> None:
            log_update(event_type, progress, status, message)

        result = await poll_enrollment_events(conn, callback=on_update, timeout=TIMEOUT)

        print("UId: ", device_uid )
        templates = await get_templates(conn)
        # Print in table format
        for t in templates[:10]:
            print(t)

        # Check if enrollment succeeded based on rechecking the fingerprint template on device after completion
        if result.get("success"):
            log.info("Verifying enrollment by checking fingerprint template on device...")
            enrolled = await finger_already_enrolled(conn, user_id_str, FINGER_ID)
            if enrolled:
                log.info("Verification successful: fingerprint template found on device.")
            else:
                log.error("Verification failed: fingerprint template NOT found on device after successful enrollment.")
                result["success"] = False
                result["message"] += " (verification failed: template not found)"

        print("-" * 60)
        print("Result:", result)
        if result.get("success"):
            print("✓ Enrollment completed successfully.")
        else:
            print("✗ Enrollment did not complete.")

    except Exception as e:
        log.error("Error: %s", e, exc_info=True)
    finally:
        try:
            await run_in_thread(conn.disconnect)
        except Exception:
            pass
        print("\nDisconnected from device.")

def main2():
    """ Capture live events without async/await, for debugging. """
    conn = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=CONNECT_TIMEOUT, password=int(DEVICE_PASSWORD) if DEVICE_PASSWORD else 0).connect()
    conn.reg_event(EF_ENROLLFINGER)
    conn.cancel_capture()
    conn._ZK__sock.settimeout(TIMEOUT)

    print("Waiting for events...")
    while True:
        try:
            data_recv = conn._ZK__sock.recv(1032)
            print("Event data:", data_recv)
            conn._ZK__ack_ok()
        except SocketTimeout:
            print("Timeout waiting for event")
            break
        except Exception as e:
            print("Error:", e)
            break


if __name__ == "__main__":
    asyncio.run(main())
    # main2()