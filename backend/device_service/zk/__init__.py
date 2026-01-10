"""
ZKTeco device integration module.

This module provides async wrappers and utilities for communicating with
ZKTeco biometric devices using the pyzk library.
"""

from device_service.zk.base import ZKDeviceConnection
from device_service.zk.const import (
    CMD_CONNECT,
    CMD_AUTH,
    CMD_USER_WRQ,
    CMD_USERTEMP_RRQ,
    CMD_USERTEMP_WRQ,
    CMD_DELETE_USER,
    CMD_ATTLOG_RRQ,
    CMD_STARTENROLL,
    CMD_CANCELCAPTURE,
    CMD_GET_TIME,
    CMD_SET_TIME,
    CMD_GET_FREE_SIZES,
    CMD_REG_EVENT,
    EF_ATTLOG,
    EF_ENROLLFINGER,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
)

__all__ = [
    "ZKDeviceConnection",
    "CMD_CONNECT",
    "CMD_AUTH",
    "CMD_USER_WRQ",
    "CMD_USERTEMP_RRQ",
    "CMD_USERTEMP_WRQ",
    "CMD_DELETE_USER",
    "CMD_ATTLOG_RRQ",
    "CMD_STARTENROLL",
    "CMD_CANCELCAPTURE",
    "CMD_GET_TIME",
    "CMD_SET_TIME",
    "CMD_GET_FREE_SIZES",
    "CMD_REG_EVENT",
    "EF_ATTLOG",
    "EF_ENROLLFINGER",
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
]

