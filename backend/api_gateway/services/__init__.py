"""Services module for API Gateway."""

from api_gateway.services.proxy_service import (
    ProxyService,
    get_school_service_proxy,
    get_device_service_proxy,
    get_attendance_service_proxy,
    get_notification_service_proxy,
)

__all__ = [
    "ProxyService",
    "get_school_service_proxy",
    "get_device_service_proxy",
    "get_attendance_service_proxy",
    "get_notification_service_proxy",
]

