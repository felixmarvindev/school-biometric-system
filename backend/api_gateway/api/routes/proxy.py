"""Proxy routes for API Gateway."""

from fastapi import APIRouter, Request, Depends
from typing import Any

from api_gateway.core.config import settings
from api_gateway.services.proxy_service import (
    get_school_service_proxy,
    get_device_service_proxy,
    get_attendance_service_proxy,
    get_notification_service_proxy,
)

router = APIRouter()


@router.api_route(
    "/api/v1/schools/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=True,
    tags=["proxy", "schools"],
)
async def proxy_school_service(
    request: Request,
    path: str = "",
    proxy: Any = Depends(lambda: get_school_service_proxy(settings)),
):
    """
    Proxy requests to School Service.
    
    Routes all requests matching /api/v1/schools/* to the School Service.
    """
    # Normalize path (remove leading slash if present)
    normalized_path = path.lstrip("/") if path else ""
    target_path = f"/api/v1/schools/{normalized_path}" if normalized_path else "/api/v1/schools"
    return await proxy.proxy_request(request, target_path)


@router.api_route(
    "/api/v1/devices/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=True,
    tags=["proxy", "devices"],
)
async def proxy_device_service(
    request: Request,
    path: str = "",
    proxy: Any = Depends(lambda: get_device_service_proxy(settings)),
):
    """
    Proxy requests to Device Service.
    
    Routes all requests matching /api/v1/devices/* to the Device Service.
    """
    # Normalize path (remove leading slash if present)
    normalized_path = path.lstrip("/") if path else ""
    target_path = f"/api/v1/devices/{normalized_path}" if normalized_path else "/api/v1/devices"
    return await proxy.proxy_request(request, target_path)


@router.api_route(
    "/api/v1/attendance/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=True,
    tags=["proxy", "attendance"],
)
async def proxy_attendance_service(
    request: Request,
    path: str = "",
    proxy: Any = Depends(lambda: get_attendance_service_proxy(settings)),
):
    """
    Proxy requests to Attendance Service.
    
    Routes all requests matching /api/v1/attendance/* to the Attendance Service.
    """
    # Normalize path (remove leading slash if present)
    normalized_path = path.lstrip("/") if path else ""
    target_path = f"/api/v1/attendance/{normalized_path}" if normalized_path else "/api/v1/attendance"
    return await proxy.proxy_request(request, target_path)


@router.api_route(
    "/api/v1/notifications/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=True,
    tags=["proxy", "notifications"],
)
async def proxy_notification_service(
    request: Request,
    path: str = "",
    proxy: Any = Depends(lambda: get_notification_service_proxy(settings)),
):
    """
    Proxy requests to Notification Service.
    
    Routes all requests matching /api/v1/notifications/* to the Notification Service.
    """
    # Normalize path (remove leading slash if present)
    normalized_path = path.lstrip("/") if path else ""
    target_path = f"/api/v1/notifications/{normalized_path}" if normalized_path else "/api/v1/notifications"
    return await proxy.proxy_request(request, target_path)

