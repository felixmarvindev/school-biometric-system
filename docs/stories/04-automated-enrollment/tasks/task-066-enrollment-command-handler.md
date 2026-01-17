# Task 066: Enrollment Command Handler

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 2: Device Control

## Description

Implement the backend service to send enrollment commands (CMD_STARTENROLL) to ZKTeco devices and handle device responses.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
2 days

## Prerequisites

- ✅ Task 065 complete (enrollment session model)
- ✅ ZKTeco device connection working
- ✅ Device service infrastructure ready

## Acceptance Criteria

1. [ ] Enrollment service created
2. [ ] Can send CMD_STARTENROLL command to device
3. [ ] Device connection handled correctly
4. [ ] Enrollment session created in database
5. [ ] Error handling for device offline
6. [ ] Error handling for connection timeout
7. [ ] Error handling for device busy
8. [ ] Enrollment cancellation support (CMD_CANCELCAPTURE)
9. [ ] Unit tests created

## Implementation Details

### Backend Changes

1. **backend/device_service/services/enrollment_service.py**
   - Create EnrollmentService class
   - Add `start_enrollment()` method
   - Add `cancel_enrollment()` method
   - Add error handling

2. **backend/device_service/zk/base.py** (if needed)
   - Add `start_enrollment()` method to ZKDeviceConnection
   - Add `cancel_enrollment()` method

3. **backend/device_service/repositories/enrollment_repository.py**
   - Create EnrollmentRepository
   - Add CRUD methods for enrollment sessions

### Key Code Patterns

```python
# backend/device_service/services/enrollment_service.py
from device_service.zk.base import ZKDeviceConnection
from device_service.zk.const import CMD_STARTENROLL, CMD_CANCELCAPTURE
from device_service.models.enrollment import EnrollmentSession, EnrollmentStatus
from device_service.repositories.enrollment_repository import EnrollmentRepository
import uuid
import logging

logger = logging.getLogger(__name__)

class EnrollmentService:
    """Service for managing enrollment operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EnrollmentRepository(db)
        self.connection_service = DeviceConnectionService(db)
    
    async def start_enrollment(
        self,
        student_id: int,
        device_id: int,
        finger_id: int,
        school_id: int,
    ) -> EnrollmentSession:
        """
        Start enrollment on a device.
        
        Args:
            student_id: Student ID
            device_id: Device ID
            finger_id: Finger ID (0-9)
            school_id: School ID
        
        Returns:
            EnrollmentSession instance
        
        Raises:
            DeviceOfflineError: If device is offline
            EnrollmentError: If enrollment fails
        """
        # Get device
        device = await self.connection_service.get_device(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        # Check device is online
        if device.status != DeviceStatus.ONLINE:
            raise DeviceOfflineError(f"Device {device_id} is offline")
        
        # Create enrollment session
        session_id = str(uuid.uuid4())
        enrollment_session = await self.repository.create({
            "session_id": session_id,
            "student_id": student_id,
            "device_id": device_id,
            "finger_id": finger_id,
            "school_id": school_id,
            "status": EnrollmentStatus.PENDING,
        })
        
        try:
            # Get device connection
            conn = await self.connection_service.get_connection(device)
            if not conn:
                raise DeviceOfflineError(f"Cannot connect to device {device_id}")
            
            # Send enrollment command
            # TODO: Implement in ZKDeviceConnection
            await conn.start_enrollment(
                user_id=student_id,  # Map student to device user ID
                finger_id=finger_id
            )
            
            # Update session status
            enrollment_session.status = EnrollmentStatus.IN_PROGRESS
            await self.db.commit()
            await self.db.refresh(enrollment_session)
            
            logger.info(
                f"Enrollment started: session={session_id}, "
                f"student={student_id}, device={device_id}, finger={finger_id}"
            )
            
            return enrollment_session
            
        except Exception as e:
            # Update session with error
            enrollment_session.status = EnrollmentStatus.FAILED
            enrollment_session.error_message = str(e)
            await self.db.commit()
            
            logger.error(f"Enrollment failed: session={session_id}, error={e}")
            raise EnrollmentError(f"Failed to start enrollment: {e}") from e
```

## Testing

### Manual Testing

1. **Start Enrollment**
   - Call start_enrollment service
   - ✅ Verify enrollment session created
   - ✅ Verify device receives command
   - ✅ Verify session status is IN_PROGRESS

2. **Error Handling**
   - Try with offline device
   - ✅ Verify DeviceOfflineError raised
   - ✅ Verify session marked as FAILED

## Definition of Done

- [ ] Enrollment service created
- [ ] Can send enrollment commands
- [ ] Error handling works
- [ ] Unit tests pass
- [ ] Integration tests pass (if possible)

## Next Task

**Task 067: Enrollment API Endpoint** - Create REST API endpoint for starting enrollment.
