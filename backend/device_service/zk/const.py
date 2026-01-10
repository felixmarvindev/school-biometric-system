"""
ZKTeco protocol command constants.

This module contains all the command constants used to communicate with ZKTeco devices.
These constants match the ZKTeco proprietary TCP/IP protocol specification.
"""

# Connection Commands
CMD_CONNECT = 1000
CMD_ACK_OK = 2000
CMD_AUTH = 1102

# User Management Commands
CMD_USER_WRQ = 8  # Write user data to device
CMD_USERTEMP_RRQ = 9  # Read user template (fingerprint)
CMD_USERTEMP_WRQ = 10  # Write user template (fingerprint)
CMD_DELETE_USER = 18  # Delete user from device
CMD_CLEAR_DATA = 20  # Clear all data (users, attendance, etc.)

# Attendance Commands
CMD_ATTLOG_RRQ = 13  # Read attendance logs
CMD_CLEAR_ATTLOG = 15  # Clear attendance logs

# Enrollment Commands
CMD_STARTENROLL = 61  # Start fingerprint enrollment mode
CMD_CANCELCAPTURE = 62  # Cancel enrollment capture

# Device Information Commands
CMD_GET_TIME = 201  # Get device time
CMD_SET_TIME = 202  # Set device time
CMD_GET_FREE_SIZES = 50  # Get device capacity (users, fingerprints, etc.)
CMD_DEVICE = 11  # Get device information
CMD_GET_VERSION = 1100  # Get firmware version

# Device Control Commands
CMD_RESTART = 1004  # Restart device
CMD_POWEROFF = 1005  # Power off device
CMD_SLEEP = 1006  # Put device to sleep
CMD_RESUME = 1007  # Resume device from sleep
CMD_CAPTUREONLY = 2001  # Capture fingerprint only (no enrollment)

# Event Registration
CMD_REG_EVENT = 500  # Register for real-time events

# Event Flags (for CMD_REG_EVENT)
EF_ATTLOG = 1  # Attendance event
EF_FINGER = (1 << 2)  # Fingerprint event
EF_ENROLLFINGER = (1 << 3)  # Fingerprint enrollment event
EF_ENROLLFACE = (1 << 4)  # Face enrollment event
EF_BUTTON = (1 << 5)  # Button press event
EF_UNLOCK = (1 << 6)  # Unlock event
EF_VERIFY = (1 << 7)  # Verification event
EF_FPFTR = (1 << 8)  # Fingerprint template event
EF_ALARM = (1 << 9)  # Alarm event

# Response Codes
CMD_ACK_OK = 2000
CMD_ACK_ERROR = 2001
CMD_ACK_DATA = 2002
CMD_ACK_RETRY = 2003
CMD_ACK_REPEAT = 2004
CMD_ACK_UNAUTH = 2005

# Device Ports
DEFAULT_PORT = 4370
DEFAULT_TIMEOUT = 5  # seconds
