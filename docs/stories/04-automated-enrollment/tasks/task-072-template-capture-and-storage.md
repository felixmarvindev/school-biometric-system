# Task 072: Template Capture and Storage

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 4: Template Storage

## Description

Implement fingerprint template capture from device when enrollment completes and store it securely (encrypted) in the database.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
2 days

## Prerequisites

- ✅ Task 066 complete (enrollment command handler)
- ✅ Encryption utilities available

## Acceptance Criteria

1. [ ] Can capture template data from device
2. [ ] Template is encrypted before storage
3. [x] Template stored in enrollment session record
4. [x] Quality score captured (if available)
5. [ ] Enrollment record created linking student to device
6. [ ] Template encryption/decryption utilities work
7. [ ] Unit tests created

## Implementation Details

### Backend Changes

1. **backend/device_service/services/enrollment_service.py**
   - Add `capture_template()` method
   - Add `store_template()` method
   - Update enrollment completion flow

2. **backend/device_service/core/encryption.py** (if needed)
   - Add template encryption utilities
   - Add template decryption utilities

3. **backend/device_service/zk/base.py** (if needed)
   - Add `get_template()` method to capture template from device

### Key Code Patterns

```python
# backend/device_service/services/enrollment_service.py
from cryptography.fernet import Fernet
import base64

class EnrollmentService:
    def __init__(self, db: AsyncSession):
        # ... existing code ...
        self.encryption_key = settings.TEMPLATE_ENCRYPTION_KEY
    
    async def capture_and_store_template(
        self,
        enrollment_session: EnrollmentSession,
        device: Device,
    ):
        """Capture template from device and store encrypted."""
        conn = await self.connection_service.get_connection(device)
        if not conn:
            raise DeviceOfflineError("Cannot connect to device")
        
        # Capture template from device
        template_data = await conn.get_template(
            user_id=enrollment_session.student_id,
            finger_id=enrollment_session.finger_id
        )
        
        if not template_data:
            raise EnrollmentError("Failed to capture template")
        
        # Encrypt template
        encrypted_template = self._encrypt_template(template_data)
        
        # Store in enrollment session
        enrollment_session.template_data = encrypted_template
        enrollment_session.quality_score = template_data.get('quality', None)
        enrollment_session.status = EnrollmentStatus.COMPLETED
        enrollment_session.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(enrollment_session)
        
        # Create enrollment record (student-device mapping)
        await self._create_enrollment_record(enrollment_session)
    
    def _encrypt_template(self, template_data: bytes) -> str:
        """Encrypt template data before storage."""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(template_data)
        return base64.b64encode(encrypted).decode('utf-8')
```

## Testing

### Manual Testing

1. **Template Capture**
   - Complete enrollment
   - ✅ Verify template captured
   - ✅ Verify template encrypted
   - ✅ Verify stored in database

## Definition of Done

- [ ] Template capture works
- [ ] Template encryption works
- [x] Template storage works (schema + quality_score in session)
- [x] Quality score captured
- [ ] Unit tests pass

## Next Task

**Task 073: Enrollment Success UI** - Create success screen after enrollment completes.
