# Technical Architecture Document

## School Biometric Management System

**Version**: 1.0  
**Last Updated**: January 2024  
**Author**: Development Team

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Service Architecture](#service-architecture)
4. [Data Architecture](#data-architecture)
5. [Device Integration](#device-integration)
6. [Real-time Communication](#real-time-communication)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Deployment Architecture](#deployment-architecture)
10. [Technology Decisions](#technology-decisions)

---

## 1. System Overview

### 1.1 Purpose

A cloud-based biometric attendance management system enabling:
- Automated remote fingerprint enrollment
- Real-time attendance tracking
- Instant parent notifications
- Centralized school management

### 1.2 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                     External Systems                         │
├─────────────────────────────────────────────────────────────┤
│  Africa's Talking SMS  │  Email Service  │  Payment Gateway │
└──────────┬─────────────┴────────┬────────┴─────────┬────────┘
           │                      │                  │
           ▼                      ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│                   School Biometric System                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Frontend   │  │   Backend    │  │   Database   │       │
│  │  (Next.js)   │  │  (FastAPI)   │  │ (PostgreSQL) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────┬─────────────────────────────────────────┬─────────┘
           │                                         │
           ▼                                         ▼
┌─────────────────────┐                   ┌──────────────────┐
│   School Admins     │                   │ ZKTeco Devices   │
│   (Web Browser)     │                   │  (On-premise)    │
└─────────────────────┘                   └──────────────────┘
```

### 1.3 Key Quality Attributes

| Attribute | Target | Rationale |
|-----------|--------|-----------|
| **Availability** | 99.5% uptime | School hours: 6 AM - 6 PM, 5 days/week |
| **Performance** | < 200ms API response | Smooth user experience |
| **Scalability** | 100+ schools, 50K+ students | Growth projection |
| **Security** | ISO 27001 aligned | Handles student PII |
| **Reliability** | Zero data loss | Attendance is critical |
| **Maintainability** | < 1 day for bug fixes | Small team, rapid iteration |

---

## 2. Architecture Patterns

### 2.1 Microservices Architecture

**Why Microservices?**
- Independent deployment and scaling
- Technology diversity (Python for device control, future Node.js services)
- Team autonomy
- Fault isolation

**Trade-offs Accepted:**
- Increased operational complexity (mitigated by Docker Compose)
- Eventual consistency in some scenarios
- Network latency between services

### 2.2 Clean Architecture (Onion Architecture)

Each service follows clean architecture principles:

```
┌──────────────────────────────────────────┐
│          Presentation Layer              │
│         (API Routes, WebSocket)          │
├──────────────────────────────────────────┤
│         Application Layer                │
│      (Use Cases, Services)               │
├──────────────────────────────────────────┤
│          Domain Layer                    │
│    (Entities, Business Logic)            │
├──────────────────────────────────────────┤
│      Infrastructure Layer                │
│  (Database, External APIs, Devices)      │
└──────────────────────────────────────────┘
```

**Benefits:**
- Testability (mock infrastructure)
- Business logic isolation
- Framework independence

### 2.3 Event-Driven Architecture

For real-time features and asynchronous processing:

```
Device Event ──▶ Redis Pub/Sub ──▶ Attendance Service ──▶ Database
                                ──▶ Notification Service ──▶ SMS Gateway
                                ──▶ WebSocket Server ──▶ Frontend
```

### 2.4 Repository Pattern

Data access abstraction:

```python
# Domain layer - interface
class IStudentRepository(ABC):
    async def get_by_id(self, student_id: int) -> Student:
        pass

# Infrastructure layer - implementation
class SQLAlchemyStudentRepository(IStudentRepository):
    async def get_by_id(self, student_id: int) -> Student:
        # Database-specific implementation
```

### 2.5 Strategy Pattern (Simulation Mode)

Device communication abstraction:

```python
# Strategy interface
class DeviceInterface(ABC):
    async def enroll_finger(...): pass

# Concrete strategies
class ZKTecoDevice(DeviceInterface):
    # Real device implementation

class SimulatedDevice(DeviceInterface):
    # Mock device for demos

# Context
def get_device(simulation: bool) -> DeviceInterface:
    return SimulatedDevice() if simulation else ZKTecoDevice()
```

---

## 3. Service Architecture

### 3.1 Service Inventory

| Service | Port | Purpose | Database | External Deps |
|---------|------|---------|----------|---------------|
| API Gateway | 8000 | Entry point, auth, routing | - | Redis |
| School Service | 8001 | School/student management | PostgreSQL | - |
| Device Service | 8002 | Device orchestration | PostgreSQL, Redis | ZKTeco devices |
| Attendance Service | 8003 | Attendance tracking | PostgreSQL | Redis |
| Notification Service | 8004 | SMS/email alerts | PostgreSQL | Africa's Talking |

### 3.2 API Gateway Service

**Responsibilities:**
- Request routing
- Authentication & authorization (JWT)
- Rate limiting
- Request/response transformation
- API versioning
- CORS handling

**Technology:**
- FastAPI
- Redis (for rate limiting, session storage)
- JWT for authentication

**Endpoints:**
```
POST   /auth/login
POST   /auth/refresh
GET    /health

# Proxied routes
/api/v1/schools/*      ──▶ School Service
/api/v1/devices/*      ──▶ Device Service
/api/v1/attendance/*   ──▶ Attendance Service
/api/v1/notifications/* ──▶ Notification Service
```

### 3.3 School Management Service

**Responsibilities:**
- School CRUD operations
- Student management
- Class and stream management
- Parent contact management
- User/admin management

**Domain Entities:**
- School
- Student
- Class
- Stream
- Parent/Guardian
- Admin User

**Key Operations:**
```python
# Student management
create_student(school_id, student_data) -> Student
get_student(student_id) -> Student
update_student(student_id, updates) -> Student
deactivate_student(student_id) -> bool
search_students(filters) -> List[Student]

# Academic structure
create_class(school_id, class_data) -> Class
assign_student_to_stream(student_id, stream_id) -> bool
```

### 3.4 Device Orchestration Service

**Responsibilities:**
- Device registration and management
- Device health monitoring
- Enrollment coordination
- Sync operations (student ↔ device)
- ZKTeco SDK integration
- Simulation mode

**Domain Entities:**
- Device
- DeviceGroup
- EnrollmentSession
- SyncOperation

**Key Operations:**
```python
# Device management
register_device(ip, port, location) -> Device
get_device_status(device_id) -> DeviceStatus
update_device_group(device_id, group_id) -> bool

# Enrollment
start_enrollment(student_id, device_id, finger_id) -> EnrollmentSession
monitor_enrollment_progress(session_id) -> EnrollmentProgress
cancel_enrollment(session_id) -> bool

# Sync operations
sync_student_to_devices(student_id, device_ids) -> SyncResult
bulk_sync_class(class_id, device_group_id) -> SyncResult
```

**Device Communication Flow:**
```
1. Admin initiates enrollment
   ↓
2. Device Service validates request
   ↓
3. Connect to device (or simulate)
   ↓
4. Send CMD_STARTENROLL command
   ↓
5. Register for EF_ENROLLFINGER event
   ↓
6. Poll for events in background
   ↓
7. Emit progress via WebSocket
   ↓
8. On completion, store fingerprint template
   ↓
9. Notify frontend
```

### 3.5 Attendance Service

**Responsibilities:**
- Attendance event processing
- Entry/Exit determination
- Attendance record storage
- Reporting and analytics
- Historical data queries

**Domain Entities:**
- AttendanceRecord
- AttendanceSession
- AttendanceReport

**Key Operations:**
```python
# Event processing
process_attendance_event(device_id, user_id, timestamp) -> AttendanceRecord
determine_entry_exit(student_id, timestamp) -> 'IN' | 'OUT'

# Queries
get_attendance_by_date(school_id, date) -> List[AttendanceRecord]
get_student_attendance_history(student_id, date_range) -> List[AttendanceRecord]
calculate_attendance_rate(student_id, period) -> float

# Reporting
generate_daily_report(school_id, date) -> Report
generate_class_summary(class_id, date_range) -> Report
```

**Entry/Exit Logic:**
```python
def determine_entry_exit(student_id: int, timestamp: datetime) -> str:
    """
    Logic:
    1. Get last attendance record for student
    2. If no previous record → 'IN'
    3. If last record was 'IN' and > 30 mins ago → 'OUT'
    4. If last record was 'OUT' → 'IN'
    5. If last record < 30 mins ago → Duplicate (ignore)
    """
```

### 3.6 Notification Service

**Responsibilities:**
- SMS notifications to parents
- Email notifications (future)
- Message templating
- Delivery tracking
- Retry logic

**Domain Entities:**
- Notification
- NotificationTemplate
- DeliveryStatus

**Key Operations:**
```python
# Notification sending
send_attendance_notification(student_id, event_type) -> Notification
send_bulk_notifications(notifications) -> List[DeliveryStatus]

# Templates
render_template(template_id, context) -> str

# Tracking
get_notification_status(notification_id) -> DeliveryStatus
retry_failed_notifications() -> int
```

**Africa's Talking Integration:**
```python
import africastalking

# Initialize
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Send message
def send_sms(phone: str, message: str) -> dict:
    response = sms.send(message, [phone], sender_id)
    return {
        'status': response['SMSMessageData']['Recipients'][0]['status'],
        'cost': response['SMSMessageData']['Recipients'][0]['cost']
    }
```

---

## 4. Data Architecture

### 4.1 Database Schema

#### Schools Table
```sql
CREATE TABLE schools (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_schools_code ON schools(code);
```

#### Students Table
```sql
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    school_id BIGINT NOT NULL REFERENCES schools(id),
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    stream_id BIGINT REFERENCES streams(id),
    parent_phone VARCHAR(20),
    parent_email VARCHAR(100),
    photo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_students_school ON students(school_id);
CREATE INDEX idx_students_admission ON students(admission_number);
CREATE INDEX idx_students_stream ON students(stream_id);
```

#### Classes and Streams
```sql
CREATE TABLE classes (
    id BIGSERIAL PRIMARY KEY,
    school_id BIGINT NOT NULL REFERENCES schools(id),
    name VARCHAR(100) NOT NULL,  -- e.g., "Grade 3", "Form 1"
    level INTEGER NOT NULL,      -- 1-12
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(school_id, name)
);

CREATE TABLE streams (
    id BIGSERIAL PRIMARY KEY,
    class_id BIGINT NOT NULL REFERENCES classes(id),
    name VARCHAR(50) NOT NULL,   -- e.g., "A", "B", "East"
    capacity INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(class_id, name)
);
```

#### Devices
```sql
CREATE TABLE devices (
    id BIGSERIAL PRIMARY KEY,
    school_id BIGINT NOT NULL REFERENCES schools(id),
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    port INTEGER DEFAULT 4370,
    location VARCHAR(200),        -- e.g., "Main Gate", "Dormitory A"
    device_group_id BIGINT REFERENCES device_groups(id),
    is_online BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_devices_school ON devices(school_id);
CREATE INDEX idx_devices_serial ON devices(serial_number);
CREATE INDEX idx_devices_group ON devices(device_group_id);

CREATE TABLE device_groups (
    id BIGSERIAL PRIMARY KEY,
    school_id BIGINT NOT NULL REFERENCES schools(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);
```

#### Enrollments
```sql
CREATE TABLE enrollments (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id),
    device_id BIGINT NOT NULL REFERENCES devices(id),
    finger_id INTEGER NOT NULL,   -- 0-9 (which finger)
    template_data BYTEA,          -- Fingerprint template
    quality_score INTEGER,        -- 0-100
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    enrolled_by BIGINT REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, device_id, finger_id)
);

CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_device ON enrollments(device_id);
```

#### Attendance Records
```sql
CREATE TABLE attendance_records (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id),
    device_id BIGINT NOT NULL REFERENCES devices(id),
    event_type VARCHAR(10) NOT NULL,  -- 'IN' or 'OUT'
    timestamp TIMESTAMPTZ NOT NULL,
    finger_id INTEGER,
    verification_method VARCHAR(20),  -- 'FINGERPRINT', 'CARD', 'MANUAL'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_attendance_timestamp ON attendance_records(timestamp);
CREATE INDEX idx_attendance_device ON attendance_records(device_id);
CREATE INDEX idx_attendance_composite ON attendance_records(student_id, timestamp);

-- Partition by month for performance
CREATE TABLE attendance_records_y2024m01 PARTITION OF attendance_records
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- ... more partitions
```

#### Notifications
```sql
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id),
    attendance_record_id BIGINT REFERENCES attendance_records(id),
    recipient_phone VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'PENDING', 'SENT', 'DELIVERED', 'FAILED'
    provider VARCHAR(50),         -- 'AFRICASTALKING', 'TWILIO'
    provider_id VARCHAR(100),
    cost DECIMAL(10, 4),
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_student ON notifications(student_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created ON notifications(created_at);
```

### 4.2 Data Partitioning Strategy

**Attendance Records: Time-based Partitioning**
- Monthly partitions
- Keeps recent data in fast tables
- Archives old data for reporting

**Notifications: Range Partitioning**
- By status (PENDING, SENT, DELIVERED, FAILED)
- Faster queries on pending notifications

### 4.3 Caching Strategy

**Redis Cache Layers:**

```
┌─────────────────────────────────────────┐
│         Application Cache (Redis)        │
├─────────────────────────────────────────┤
│  Device Status Cache (TTL: 30s)         │
│  Student Lookup Cache (TTL: 5m)         │
│  Attendance Today Cache (TTL: 1m)       │
│  Session/JWT Cache (TTL: 30m)           │
└─────────────────────────────────────────┘
```

**Cache Invalidation:**
- Device status: Automatic expiry (30 seconds)
- Student data: Invalidate on update
- Attendance: Invalidate on new event
- Session: Invalidate on logout

### 4.4 Data Retention

| Data Type | Retention | Archive Strategy |
|-----------|-----------|------------------|
| Attendance Records | 7 years | Move to cold storage after 2 years |
| Notifications | 1 year | Delete after 1 year |
| Audit Logs | 5 years | Compress and archive |
| Student Records | Permanent | Soft delete only |
| Device Logs | 90 days | Rolling deletion |

---

## 5. Device Integration

### 5.1 ZKTeco Protocol

The system communicates with ZKTeco devices using their proprietary TCP/IP protocol.

**Connection Flow:**
```
1. TCP connection on port 4370
2. Send CMD_CONNECT (1000)
3. Receive CMD_ACK_OK (2000)
4. Send CMD_AUTH (1102) with password
5. Receive CMD_ACK_OK
6. Connection established
```

**Key Commands Used:**
```python
# Enrollment
CMD_STARTENROLL = 61     # Put device in enrollment mode
CMD_CANCELCAPTURE = 62   # Cancel enrollment
CMD_USER_WRQ = 8         # Upload user to device
CMD_USERTEMP_WRQ = 10    # Upload fingerprint template

# Attendance
CMD_ATTLOG_RRQ = 13      # Read attendance logs
CMD_CLEAR_ATTLOG = 15    # Clear attendance logs

# Events
CMD_REG_EVENT = 500      # Register for real-time events
EF_ATTLOG = 1            # Attendance event flag
EF_ENROLLFINGER = 8      # Enrollment event flag

# Device management
CMD_GET_TIME = 201       # Get device time
CMD_SET_TIME = 202       # Set device time
CMD_RESTART = 1004       # Restart device
CMD_GET_FREE_SIZES = 50  # Get capacity info
```

### 5.2 Device Communication Patterns

#### Pattern 1: Request-Response
```python
async def get_device_time(device_id: int) -> datetime:
    device = await get_device_connection(device_id)
    response = await device.send_command(CMD_GET_TIME)
    return parse_time(response)
```

#### Pattern 2: Event Listening
```python
async def listen_for_events(device_id: int):
    device = await get_device_connection(device_id)
    await device.register_event(EF_ATTLOG | EF_ENROLLFINGER)
    
    while True:
        event = await device.poll_event()
        await process_event(event)
```

#### Pattern 3: Bulk Operations
```python
async def sync_students_to_device(student_ids: List[int], device_id: int):
    device = await get_device_connection(device_id)
    
    # Batch upload
    for student_id in student_ids:
        user_data = await get_user_data(student_id)
        await device.upload_user(user_data)
    
    await device.refresh_data()  # CMD_REFRESHDATA
```

### 5.3 Simulation Architecture

**Simulation Mode Components:**

```python
# Abstraction layer
class DeviceInterface(ABC):
    async def connect(self) -> bool: pass
    async def enroll(self, user_id, finger_id) -> dict: pass
    async def get_attendance(self) -> List[AttendanceRecord]: pass

# Real implementation
class ZKTecoDevice(DeviceInterface):
    def __init__(self, ip: str, port: int):
        self.zk = ZK(ip, port)
    
    async def enroll(self, user_id, finger_id):
        # Actual ZKTeco SDK calls
        await self.zk.start_enrollment(user_id, finger_id)

# Simulated implementation
class SimulatedDevice(DeviceInterface):
    def __init__(self, device_id: int):
        self.device_id = device_id
        self.state = "idle"
    
    async def enroll(self, user_id, finger_id):
        # Simulate realistic behavior
        self.state = "enrolling"
        await self._emit_progress(user_id, 0, "Ready")
        await asyncio.sleep(1)
        await self._emit_progress(user_id, 33, "Place finger")
        await asyncio.sleep(2)
        await self._emit_progress(user_id, 66, "Hold still")
        await asyncio.sleep(1)
        await self._emit_progress(user_id, 100, "Complete")
        self.state = "idle"
        
        return {
            "success": True,
            "template": self._generate_fake_template()
        }
```

**Feature Flags:**
```python
# config.py
SIMULATION_MODE = env.bool("SIMULATION_MODE", default=True)
SIMULATION_SUCCESS_RATE = env.float("SIMULATION_SUCCESS_RATE", default=0.95)
SIMULATION_DELAY_MIN = env.float("SIMULATION_DELAY_MIN", default=1.0)
SIMULATION_DELAY_MAX = env.float("SIMULATION_DELAY_MAX", default=3.0)
```

---

## 6. Real-time Communication

### 6.1 WebSocket Architecture

**Socket.IO Implementation:**

```python
# Backend
from socketio import AsyncServer

sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Rooms for targeted broadcasting
@sio.event
async def connect(sid, environ):
    # Authenticate
    token = environ.get('HTTP_AUTHORIZATION')
    user = await verify_token(token)
    
    # Join school room
    await sio.enter_room(sid, f"school_{user.school_id}")

# Emit to specific school
async def broadcast_to_school(school_id: int, event: str, data: dict):
    await sio.emit(event, data, room=f"school_{school_id}")
```

**Frontend:**
```typescript
import { io } from 'socket.io-client';

const socket = io(WS_URL, {
  auth: { token: getAuthToken() },
  transports: ['websocket']
});

// Subscribe to enrollment updates
socket.on('enrollment_progress', (data) => {
  updateEnrollmentUI(data);
});

// Subscribe to attendance events
socket.on('attendance_event', (data) => {
  addToAttendanceList(data);
});
```

### 6.2 Event Types

#### Enrollment Progress
```typescript
interface EnrollmentProgress {
  session_id: string;
  student_id: number;
  device_id: number;
  status: 'ready' | 'in_progress' | 'complete' | 'failed' | 'cancelled';
  progress: number;  // 0-100
  message: string;
  timestamp: string;
}
```

#### Attendance Event
```typescript
interface AttendanceEvent {
  id: number;
  student_id: number;
  student_name: string;
  device_id: number;
  device_name: string;
  event_type: 'IN' | 'OUT';
  timestamp: string;
  verification_method: string;
}
```

#### Device Status
```typescript
interface DeviceStatus {
  device_id: number;
  is_online: boolean;
  last_seen: string;
  enrolled_count: number;
  capacity: number;
}
```

### 6.3 Message Flow

```
Device Event ──▶ Device Service ──▶ Redis Pub/Sub ──┬──▶ Attendance Service
                                                     │
                                                     ├──▶ Notification Service
                                                     │
                                                     └──▶ WebSocket Server ──▶ Frontend
```

---

## 7. Security Architecture

### 7.1 Authentication & Authorization

**JWT-based Authentication:**
```python
from jose import jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token generation
def create_access_token(user_id: int, school_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "school_id": school_id,
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Token verification
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    return await get_user_by_id(int(user_id))
```

**Role-Based Access Control:**
```python
class Permission(str, Enum):
    VIEW_STUDENTS = "students:read"
    MANAGE_STUDENTS = "students:write"
    ENROLL_STUDENTS = "enrollment:write"
    VIEW_ATTENDANCE = "attendance:read"
    MANAGE_DEVICES = "devices:write"

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [all permissions],
    Role.SCHOOL_ADMIN: [
        Permission.VIEW_STUDENTS,
        Permission.MANAGE_STUDENTS,
        Permission.ENROLL_STUDENTS,
        Permission.VIEW_ATTENDANCE,
        Permission.MANAGE_DEVICES
    ],
    Role.TEACHER: [
        Permission.VIEW_STUDENTS,
        Permission.VIEW_ATTENDANCE
    ],
    Role.VIEWER: [
        Permission.VIEW_STUDENTS,
        Permission.VIEW_ATTENDANCE
    ]
}

def require_permission(permission: Permission):
    def decorator(func):
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### 7.2 Data Protection

**Encryption at Rest:**
- Database: PostgreSQL encryption (TDE)
- Backups: AES-256 encryption
- Fingerprint templates: Encrypted before storage

**Encryption in Transit:**
- HTTPS/TLS 1.3 for all API communication
- WSS for WebSocket connections
- VPN tunnel for device communication (optional)

**PII Protection:**
```python
# Sensitive fields
SENSITIVE_FIELDS = [
    'student.date_of_birth',
    'student.parent_phone',
    'student.parent_email',
    'enrollment.template_data'
]

# Audit logging
@audit_log(action="view_pii")
async def get_student_details(student_id: int, current_user: User):
    # Log who accessed PII and when
    pass
```

### 7.3 API Security

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/students")
@limiter.limit("100/minute")
async def get_students():
    pass

@app.post("/api/enrollment")
@limiter.limit("10/minute")  # More restrictive for writes
async def start_enrollment():
    pass
```

**Input Validation:**
```python
from pydantic import BaseModel, Field, validator

class StudentCreate(BaseModel):
    admission_number: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    parent_phone: str = Field(..., regex=r'^\+?[0-9]{10,15}$')
    
    @validator('admission_number')
    def validate_admission(cls, v):
        # Custom validation
        if not v.isalnum():
            raise ValueError('Admission number must be alphanumeric')
        return v.upper()
```

**SQL Injection Prevention:**
```python
# BAD - vulnerable
query = f"SELECT * FROM students WHERE id = {student_id}"

# GOOD - parameterized
query = select(Student).where(Student.id == student_id)
```

### 7.4 Audit Logging

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    action = Column(String(50))  # 'CREATE', 'UPDATE', 'DELETE', 'VIEW'
    entity_type = Column(String(50))  # 'STUDENT', 'DEVICE', 'ENROLLMENT'
    entity_id = Column(BigInteger)
    changes = Column(JSON)  # Before/after for updates
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Usage
@audit_log(action="DELETE", entity_type="STUDENT")
async def delete_student(student_id: int, current_user: User):
    # Automatically logs the operation
    pass
```

---

## 8. Scalability & Performance

### 8.1 Horizontal Scaling

**Stateless Services:**
- All services are stateless
- State stored in Redis/PostgreSQL
- Can scale horizontally behind load balancer

**Load Balancing:**
```
                    ┌──────────────┐
                    │ Load Balancer│
                    │   (Nginx)    │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │ API Gateway │ │ API Gateway│ │ API Gateway│
    │  Instance 1 │ │ Instance 2 │ │ Instance 3 │
    └─────────────┘ └────────────┘ └────────────┘
```

### 8.2 Database Performance

**Indexing Strategy:**
- All foreign keys indexed
- Composite indexes for common queries
- Partial indexes for active records

**Query Optimization:**
```python
# Eager loading to prevent N+1
students = await db.execute(
    select(Student)
    .options(
        selectinload(Student.stream)
        .selectinload(Stream.class_)
    )
    .where(Student.school_id == school_id)
)

# Pagination
students = await db.execute(
    select(Student)
    .offset(page * page_size)
    .limit(page_size)
)
```

**Connection Pooling:**
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 8.3 Caching Strategy

**Cache Hierarchy:**
```
┌─────────────────────────────────┐
│      Application Cache          │
│         (Redis)                 │
│  - Device status (30s TTL)      │
│  - Student lookup (5m TTL)      │
│  - Attendance today (1m TTL)    │
└───────────┬─────────────────────┘
            │
┌───────────▼─────────────────────┐
│     Database Query Cache        │
│     (PostgreSQL shared_buffers) │
└───────────┬─────────────────────┘
            │
┌───────────▼─────────────────────┐
│       Disk Storage              │
└─────────────────────────────────┘
```

**Cache Patterns:**
```python
# Cache-aside pattern
async def get_student(student_id: int) -> Student:
    # Try cache first
    cached = await redis.get(f"student:{student_id}")
    if cached:
        return Student.parse_raw(cached)
    
    # Fallback to database
    student = await db.get(Student, student_id)
    
    # Update cache
    await redis.setex(
        f"student:{student_id}",
        300,  # 5 minutes
        student.json()
    )
    
    return student
```

### 8.4 Background Processing

**Celery Tasks:**
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def send_bulk_notifications(notification_ids: List[int]):
    """Send notifications asynchronously"""
    for notification_id in notification_ids:
        send_notification(notification_id)

@celery.task(rate_limit='100/m')
def sync_device_data(device_id: int):
    """Periodic device synchronization"""
    sync_device(device_id)

# Periodic tasks
celery.conf.beat_schedule = {
    'sync-devices-every-5-minutes': {
        'task': 'tasks.sync_all_devices',
        'schedule': 300.0
    },
    'retry-failed-notifications': {
        'task': 'tasks.retry_failed_notifications',
        'schedule': 600.0
    }
}
```

---

## 9. Deployment Architecture

### 9.1 Development Environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: school_biometric
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api-gateway:
    build: ./backend/api_gateway
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/school_biometric
      - REDIS_URL=redis://redis:6379/0

  # Other services...

volumes:
  postgres_data:
```

### 9.2 Production Architecture (AWS Example)

```
┌────────────────────────────────────────────────────────┐
│                    Route 53 (DNS)                       │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│              CloudFront (CDN)                           │
│         Static Assets + Next.js Pages                   │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│         Application Load Balancer (ALB)                 │
│              SSL Termination                            │
└──────┬───────────────────────────────────┬─────────────┘
       │                                   │
┌──────▼──────────┐              ┌────────▼────────────┐
│  ECS Fargate    │              │   ECS Fargate       │
│  API Services   │              │   Frontend          │
│  (Containers)   │              │   (Next.js)         │
└──────┬──────────┘              └─────────────────────┘
       │
       ├─────┬──────┬──────┬──────┐
       │     │      │      │      │
   ┌───▼─┐ ┌▼───┐ ┌▼───┐ ┌▼───┐ ┌▼───────────┐
   │ API │ │Sch │ │Dev │ │Att │ │   Notify   │
   │ GW  │ │Svc │ │Svc │ │Svc │ │   Service  │
   └─────┘ └────┘ └────┘ └────┘ └─────┬──────┘
                                       │
┌──────────────────────────────────────▼─────┐
│              RDS PostgreSQL                 │
│         (Multi-AZ, Auto-scaling)            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│           ElastiCache Redis                  │
│          (Cluster Mode)                      │
└─────────────────────────────────────────────┘
```

### 9.3 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pytest tests/
      
  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: docker build -t api-gateway ./backend/api_gateway
      
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login ...
          docker push api-gateway
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster prod --service api-gateway
```

---

## 10. Technology Decisions

### 10.1 Decision Log

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|---------|-----------|
| Backend Language | Python, Node.js, Java | **Python** | - Existing ZKTeco SDK<br>- Fast development<br>- Strong async support |
| Backend Framework | Django, Flask, FastAPI | **FastAPI** | - Async/await native<br>- Auto OpenAPI docs<br>- Type safety<br>- WebSocket support |
| Frontend Framework | Next.js, React+Vite, Vue | **Next.js** | - SSR capabilities<br>- File-based routing<br>- API routes<br>- Great DX |
| Database | PostgreSQL, MySQL, MongoDB | **PostgreSQL** | - ACID compliance<br>- JSON support<br>- Rich indexing<br>- Partitioning |
| Cache/Queue | Redis, RabbitMQ, Kafka | **Redis** | - Simple setup<br>- Pub/sub support<br>- Low latency<br>- Versatile |
| ORM | SQLAlchemy, Tortoise, Raw SQL | **SQLAlchemy 2.0** | - Mature ecosystem<br>- Async support<br>- Complex queries<br>- Type hints |
| WebSocket | Socket.IO, native WS | **Socket.IO** | - Room support<br>- Auto-reconnect<br>- Fallback transports |
| SMS Provider | Twilio, Africa's Talking | **Africa's Talking** | - Kenya-focused<br>- Lower costs<br>- Local support |
| Styling | Tailwind, MUI, Bootstrap | **Tailwind + shadcn/ui** | - Utility-first<br>- Customizable<br>- Modern design |

### 10.2 Trade-offs

#### Microservices vs Monolith
**Chose: Microservices**
- ✅ Independent scaling
- ✅ Technology flexibility
- ✅ Fault isolation
- ❌ Operational complexity (mitigated with Docker Compose)
- ❌ Network latency (acceptable for our use case)

#### Python vs Node.js
**Chose: Python**
- ✅ Existing ZKTeco library
- ✅ Strong async support
- ✅ Data science capabilities (future analytics)
- ❌ Slightly slower than Node.js (negligible in our context)

#### SQL vs NoSQL
**Chose: PostgreSQL (SQL)**
- ✅ ACID transactions (critical for attendance)
- ✅ Complex queries (reporting)
- ✅ Data integrity
- ❌ Schema migrations (manageable with Alembic)

---

**End of Technical Architecture Document**
