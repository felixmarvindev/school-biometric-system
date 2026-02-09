"""WebSocket routes for real-time device status updates."""

import logging
from fastapi import WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi import APIRouter

from device_service.api.dependencies import get_current_user_ws
from device_service.services.device_status_broadcaster import broadcaster
from device_service.services.enrollment_progress_broadcaster import enrollment_broadcaster

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket status codes
WS_1008_POLICY_VIOLATION = 1008
WS_1011_INTERNAL_ERROR = 1011


@router.websocket("/ws/device-status")
async def device_status_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
):
    """
    WebSocket endpoint for real-time device status updates.
    
    Clients connect and receive events when device status changes.
    Only receives updates for devices in the authenticated user's school.
    
    Authentication is required via query parameter: `?token=<jwt_token>`
    
    Messages sent to client:
    - {"type": "connected", "message": "...", "school_id": 1}
    - {"type": "device_status_update", "device_id": 1, "status": "online", "last_seen": "...", "timestamp": "..."}
    - {"type": "device_info_update", "device_id": 1, "info": {...}, "timestamp": "..."}
      Where "info" contains: serial_number, device_name, firmware_version, device_time, capacity
    
    Example connection:
        ws://localhost:8002/ws/device-status?token=<jwt_token>
    """
    logger.info("=" * 50)
    logger.info(f"WebSocket handler called - token present: {bool(token)}")
    
    # Accept connection first (required by FastAPI)
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
    except Exception as accept_err:
        logger.error(f"Failed to accept WebSocket: {accept_err}", exc_info=True)
        return
    
    try:
        # Authenticate user via WebSocket after accepting
        logger.info("Authenticating user...")
        user = await get_current_user_ws(token)
        logger.info(f"Authentication result: user={user.id if user else None}")
        
        if not user:
            logger.warning("WebSocket authentication failed: user not found")
            await websocket.close(code=WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return
        
        school_id = user.school_id
        logger.info(f"WebSocket authenticated: user_id={user.id}, school_id={school_id}")
        
        # Register with broadcaster (without accepting again - already accepted)
        broadcaster.register(websocket, school_id)
        
        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connected",
                "message": "Connected to device status updates",
                "school_id": school_id,
            })
            
            logger.info(f"WebSocket client connected: user_id={user.id}, school_id={school_id}")
            
            # Keep connection alive and handle incoming messages (ping/pong, etc.)
            while True:
                try:
                    # Wait for any message from client (ping, etc.)
                    data = await websocket.receive_text()
                    logger.debug(f"Received WebSocket message from client: {data}")
                    
                    # Handle ping/pong or other client messages if needed
                    if data == "ping":
                        await websocket.send_json({"type": "pong"})
                        
                except WebSocketDisconnect:
                    break
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: user_id={user.id}, school_id={school_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
        finally:
            # Remove connection
            broadcaster.disconnect(websocket, school_id)
            
    except HTTPException as e:
        logger.warning(f"WebSocket authentication failed: {e.detail}")
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}", exc_info=True)
        await websocket.close(code=WS_1011_INTERNAL_ERROR)


@router.websocket("/ws/enrollment")
async def enrollment_progress_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    session_id: str = Query(None, description="Optional enrollment session ID to filter events"),
):
    """
    WebSocket endpoint for real-time enrollment progress updates.
    
    Clients connect and receive events when enrollment progress changes.
    Only receives updates for enrollments in the authenticated user's school.
    
    Authentication is required via query parameter: `?token=<jwt_token>`
    Optionally filter by session: `?token=<jwt_token>&session_id=<session_id>`
    
    Messages sent to client:
    - {"type": "connected", "message": "...", "school_id": 1, "session_id": "..."}
    - {"type": "enrollment_progress", "session_id": "...", "progress": 33, "status": "placing", "message": "...", "timestamp": "..."}
    - {"type": "enrollment_complete", "session_id": "...", "progress": 100, "status": "complete", "message": "...", "quality_score": 85, "timestamp": "..."}
    - {"type": "enrollment_error", "session_id": "...", "status": "error", "error": "...", "timestamp": "..."}
    
    Example connection:
        ws://localhost:8002/ws/enrollment?token=<jwt_token>
        ws://localhost:8002/ws/enrollment?token=<jwt_token>&session_id=<session_id>
    """
    logger.info("=" * 50)
    logger.info(f"Enrollment WebSocket handler called - token present: {bool(token)}, session_id: {session_id}")
    
    # Accept connection first (required by FastAPI)
    try:
        await websocket.accept()
        logger.info("Enrollment WebSocket connection accepted")
    except Exception as accept_err:
        logger.error(f"Failed to accept Enrollment WebSocket: {accept_err}", exc_info=True)
        return
    
    try:
        # Authenticate user via WebSocket after accepting
        logger.info("Authenticating user...")
        user = await get_current_user_ws(token)
        logger.info(f"Authentication result: user={user.id if user else None}")
        
        if not user:
            logger.warning("Enrollment WebSocket authentication failed: user not found")
            await websocket.close(code=WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return
        
        school_id = user.school_id
        logger.info(f"Enrollment WebSocket authenticated: user_id={user.id}, school_id={school_id}")
        
        # Register with enrollment broadcaster
        enrollment_broadcaster.register(websocket, school_id)
        
        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connected",
                "message": "Connected to enrollment progress updates",
                "school_id": school_id,
                "session_id": session_id,
            })
            
            logger.info(
                f"Enrollment WebSocket client connected: user_id={user.id}, "
                f"school_id={school_id}, session_id={session_id}"
            )
            
            # Keep connection alive and handle incoming messages (ping/pong, etc.)
            while True:
                try:
                    # Wait for any message from client (ping, etc.)
                    data = await websocket.receive_text()
                    logger.debug(f"Received Enrollment WebSocket message from client: {data}")
                    
                    # Handle ping/pong or other client messages if needed
                    if data == "ping":
                        await websocket.send_json({"type": "pong"})
                        
                except WebSocketDisconnect:
                    break
                    
        except WebSocketDisconnect:
            logger.info(
                f"Enrollment WebSocket client disconnected: user_id={user.id}, "
                f"school_id={school_id}, session_id={session_id}"
            )
        except Exception as e:
            logger.error(f"Enrollment WebSocket error: {e}", exc_info=True)
        finally:
            # Remove connection
            enrollment_broadcaster.disconnect(websocket, school_id)
            
    except HTTPException as e:
        logger.warning(f"Enrollment WebSocket authentication failed: {e.detail}")
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
    except Exception as e:
        logger.error(f"Enrollment WebSocket connection error: {e}", exc_info=True)
        await websocket.close(code=WS_1011_INTERNAL_ERROR)

