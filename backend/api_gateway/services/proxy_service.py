"""HTTP Proxy Service for API Gateway routing."""

import httpx
from fastapi import Request, Response, HTTPException, status
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ProxyService:
    """Service for proxying requests to backend microservices."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize proxy service.

        Args:
            base_url: Base URL of the target service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def proxy_request(
        self,
        request: Request,
        path: str,
        method: Optional[str] = None,
    ) -> Response:
        """
        Proxy HTTP request to target service.

        Args:
            request: Original FastAPI request
            path: Path to append to base URL (e.g., "/api/v1/schools/register")
            method: HTTP method (defaults to request method)

        Returns:
            FastAPI Response object
        """
        method = method or request.method
        target_url = f"{self.base_url}{path}"

        # Get request body if present
        body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
            except Exception as e:
                logger.warning(f"Error reading request body: {e}")

        # Prepare headers (exclude host and connection)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("connection", None)
        headers.pop("content-length", None)  # Let httpx set this

        try:
            # Make request to target service
            response = await self.client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )

            # Prepare response headers (exclude connection)
            response_headers = dict(response.headers)
            response_headers.pop("connection", None)
            response_headers.pop("content-encoding", None)  # Let FastAPI handle encoding

            # Return FastAPI Response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type"),
            )

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to {target_url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Service timeout: {self.base_url}",
            )
        except httpx.ConnectError:
            logger.error(f"Connection error to {target_url}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {self.base_url}",
            )
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gateway error: {str(e)}",
            )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Service instances (will be initialized with config)
_school_service_proxy: Optional[ProxyService] = None
_device_service_proxy: Optional[ProxyService] = None
_attendance_service_proxy: Optional[ProxyService] = None
_notification_service_proxy: Optional[ProxyService] = None


def get_school_service_proxy(settings) -> ProxyService:
    """Get or create School Service proxy."""
    global _school_service_proxy
    if _school_service_proxy is None:
        _school_service_proxy = ProxyService(settings.SCHOOL_SERVICE_URL)
    return _school_service_proxy


def get_device_service_proxy(settings) -> ProxyService:
    """Get or create Device Service proxy."""
    global _device_service_proxy
    if _device_service_proxy is None:
        _device_service_proxy = ProxyService(settings.DEVICE_SERVICE_URL)
    return _device_service_proxy


def get_attendance_service_proxy(settings) -> ProxyService:
    """Get or create Attendance Service proxy."""
    global _attendance_service_proxy
    if _attendance_service_proxy is None:
        _attendance_service_proxy = ProxyService(settings.ATTENDANCE_SERVICE_URL)
    return _attendance_service_proxy


def get_notification_service_proxy(settings) -> ProxyService:
    """Get or create Notification Service proxy."""
    global _notification_service_proxy
    if _notification_service_proxy is None:
        _notification_service_proxy = ProxyService(settings.NOTIFICATION_SERVICE_URL)
    return _notification_service_proxy

