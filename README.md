# School Biometric Management System

A comprehensive biometric attendance management platform for primary and secondary schools, featuring automated fingerprint enrollment and real-time parent notifications.

## 🎯 Project Vision

Transform school attendance management through automated biometric tracking, providing schools with:
- **Automated remote fingerprint enrollment** - Enroll students from the web interface
- **Real-time attendance tracking** - Know exactly when students arrive and leave
- **Instant parent notifications** - SMS alerts for every check-in/check-out
- **Scalable foundation** - Built to grow into a complete school management platform

## ✨ Key Features

### Phase 1 (MVP - Current Focus)
- 🏫 Multi-school management
- 👨‍🎓 Student registration and management
- 📚 Class and stream organization
- 🔐 **Automated fingerprint enrollment** (remotely controlled)
- 📱 Device management and monitoring
- ✅ Attendance tracking (IN/OUT)
- 📲 SMS notifications to parents
- 🎭 **Demo mode** (simulation without physical devices)

### Future Phases
- 💰 Fee management
- 📊 Academic performance tracking
- 👩‍🏫 Teacher attendance
- 📅 Timetable management
- 📈 Advanced analytics and reporting
- 🌐 Parent portal

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Frontend                        │
│          (React, TypeScript, Tailwind, shadcn/ui)           │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API & WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                   API Gateway (FastAPI)                      │
│            Authentication • Routing • Rate Limiting          │
└─────┬──────────────┬──────────────┬──────────────┬─────────┘
      │              │              │              │
┌─────▼─────┐  ┌────▼─────┐  ┌────▼──────┐  ┌────▼─────────┐
│  School   │  │  Device  │  │Attendance │  │ Notification │
│  Service  │  │  Service │  │  Service  │  │   Service    │
└───────────┘  └────┬─────┘  └───────────┘  └──────────────┘
                    │
            ┌───────▼────────┐
            │ ZKTeco Devices │
            │  (Fingerprint) │
            └────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand
- **API**: TanStack Query + Axios
- **Real-time**: Socket.IO Client

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **Cache**: Redis
- **ORM**: SQLAlchemy 2.0 (async)
- **WebSocket**: python-socketio
- **Queue**: Celery
- **Device SDK**: ZKTeco Python Library

### DevOps
- **Containers**: Docker + Docker Compose
- **Database Migrations**: Alembic
- **API Docs**: OpenAPI/Swagger (auto-generated)

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **Docker**: 24.x or higher
- **Docker Compose**: 2.x or higher
- **PostgreSQL**: 15+ (via Docker)
- **Redis**: 7+ (via Docker)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd school-biometric-system
```

### 2. Set Up Environment Variables

#### Backend
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

#### Frontend
```bash
cd frontend
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

### 3. Start Development Environment

```bash
# From project root
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- PgAdmin (port 5050)

### 4. Set Up Backend Services

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start API Gateway
cd api_gateway
uvicorn main:app --reload --port 8000

# In separate terminals, start other services:
# - School Service (port 8001)
# - Device Service (port 8002)
# - Attendance Service (port 8003)
# - Notification Service (port 8004)
```

### 5. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 📁 Project Structure

```
school-biometric-system/
├── frontend/                    # Next.js application
│   ├── app/                    # App router pages
│   │   ├── (dashboard)/       # Dashboard routes
│   │   │   ├── schools/
│   │   │   ├── students/
│   │   │   ├── devices/
│   │   │   ├── enrollment/
│   │   │   └── attendance/
│   │   └── api/               # API routes
│   ├── components/            # Reusable components
│   │   ├── ui/               # shadcn/ui components
│   │   └── features/         # Feature-specific components
│   ├── lib/                  # Utilities and helpers
│   │   ├── api/             # API client
│   │   └── hooks/           # Custom React hooks
│   └── public/              # Static assets
│
├── backend/
│   ├── api_gateway/          # API Gateway service
│   │   ├── api/
│   │   ├── core/
│   │   └── main.py
│   │
│   ├── school_service/       # School management
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── device_service/       # Device orchestration
│   │   ├── api/
│   │   ├── zk/              # ZKTeco library
│   │   ├── services/
│   │   │   ├── device_manager.py
│   │   │   └── simulator.py
│   │   └── main.py
│   │
│   ├── attendance_service/   # Attendance tracking
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── notification_service/ # SMS notifications
│   │   ├── api/
│   │   ├── services/
│   │   │   └── sms_gateway.py
│   │   └── main.py
│   │
│   ├── shared/              # Shared utilities
│   │   ├── database/
│   │   ├── schemas/
│   │   └── utils/
│   │
│   └── alembic/            # Database migrations
│
├── docker-compose.yml       # Development stack
├── .cursor_project_rules    # Cursor AI configuration
└── README.md
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/school_biometric

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
SIMULATION_MODE=true              # Enable for demo without devices
DEFAULT_DEVICE_TIMEOUT=5

# SMS Gateway (Africa's Talking)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-api-key
AFRICASTALKING_SENDER_ID=SchoolBio

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=School Biometric System
```

## 🎮 Demo Mode (Simulation)

The system can run in **simulation mode** for demonstrations without physical biometric devices.

### Enabling Simulation Mode

```bash
# In backend/.env
SIMULATION_MODE=true
```

### What Gets Simulated
- ✅ Device connection status
- ✅ Fingerprint enrollment process
- ✅ Attendance check-in/check-out events
- ✅ Real-time WebSocket updates
- ✅ Success/failure scenarios (configurable)

### Benefits
- 🎯 Sales demonstrations
- 🧪 Testing and development
- 📊 UI/UX validation
- 🎓 Training sessions

When real devices are connected, simply set `SIMULATION_MODE=false` - the rest of the system remains unchanged.

## 🧪 Testing

### Backend Tests
```bash
cd backend/school_service
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔐 Security Features

- ✅ JWT-based authentication
- ✅ Role-based access control (RBAC)
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ CORS protection
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Audit logging

## 📊 Database Schema

### Core Entities
- **Schools** - School registration and configuration
- **Students** - Student profiles and details
- **Classes** - Academic classes (Grade 1, Form 2, etc.)
- **Streams** - Class subdivisions (A, B, C)
- **Devices** - Biometric device registration
- **Device Groups** - Logical device grouping
- **Enrollments** - Student-device fingerprint mappings
- **Attendance Records** - Check-in/check-out events
- **Notifications** - SMS delivery tracking

### Relationships
```
School 1──────▶ * Student
School 1──────▶ * Device
School 1──────▶ * Class
Class 1───────▶ * Stream
Student *─────▶ * Device (via Enrollment)
Student 1─────▶ * AttendanceRecord
Device 1──────▶ * AttendanceRecord
```

## 🔄 Real-time Features

### WebSocket Events

#### Enrollment Progress
```javascript
// Client subscribes
socket.on('enrollment_progress', (data) => {
  console.log(data);
  // {
  //   student_id: 123,
  //   status: 'in_progress',
  //   progress: 60,
  //   message: 'Place finger on sensor',
  //   timestamp: '2024-01-15T10:30:00Z'
  // }
});
```

#### Attendance Events
```javascript
socket.on('attendance_event', (data) => {
  console.log(data);
  // {
  //   student_id: 123,
  //   device_id: 5,
  //   type: 'IN',
  //   timestamp: '2024-01-15T07:45:00Z'
  // }
});
```

## 📱 SMS Notifications

### Africa's Talking Integration

The system uses Africa's Talking for SMS delivery.

#### Message Templates

**Check-in notification:**
```
John Doe signed IN at 7:35 AM via Main Gate.
```

**Check-out notification:**
```
John Doe signed OUT at 4:12 PM via Main Gate.
```

### Configuration
```python
# notification_service/config.py
AFRICASTALKING_USERNAME = "your-username"
AFRICASTALKING_API_KEY = "your-api-key"
AFRICASTALKING_SENDER_ID = "SchoolBio"
```

## 🚢 Deployment

### Production Checklist

- [ ] Set `SIMULATION_MODE=false`
- [ ] Configure production database
- [ ] Set secure `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure production CORS
- [ ] Set up database backups
- [ ] Configure logging (Sentry, CloudWatch)
- [ ] Enable health checks
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure rate limiting
- [ ] Test SMS delivery
- [ ] Verify device connectivity

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 Troubleshooting

### Common Issues

#### Device Connection Fails
```bash
# Check device is online
ping <device-ip>

# Verify port is open
telnet <device-ip> 4370

# Check firewall settings
# Ensure port 4370 is not blocked
```

#### Database Connection Error
```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

#### WebSocket Not Connecting
```bash
# Verify Socket.IO server is running
curl http://localhost:8000/socket.io/

# Check CORS settings
# Ensure frontend origin is in ALLOWED_ORIGINS
```

## 📖 Development Workflow

### Adding a New Feature

1. Create feature branch
```bash
git checkout -b feature/new-feature-name
```

2. Implement backend (if needed)
```bash
cd backend/appropriate-service
# Add models, services, routes
```

3. Implement frontend
```bash
cd frontend
# Add components, pages, API calls
```

4. Write tests
```bash
# Backend
pytest tests/

# Frontend
npm run test
```

5. Create pull request
```bash
git push origin feature/new-feature-name
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes (follow commit message convention)
4. Push to the branch
5. Open a Pull Request

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📄 License

[Specify License Here]

## 👥 Team

- **Project Lead**: [Name]
- **Backend Developer**: [Name]
- **Frontend Developer**: [Name]
- **DevOps Engineer**: [Name]

## 📞 Support

For issues and questions:
- 📧 Email: support@schoolbiometric.com
- 📱 Phone: +254 XXX XXX XXX
- 💬 Slack: [workspace-url]

## 🗺️ Roadmap

### Q1 2024
- [x] Project setup
- [x] Database schema design
- [ ] School & student management
- [ ] Device integration (simulation)
- [ ] Basic attendance tracking

### Q2 2024
- [ ] Automated enrollment
- [ ] Real-time WebSocket updates
- [ ] SMS notifications
- [ ] Device group management
- [ ] Beta testing with 3 schools

### Q3 2024
- [ ] Production deployment
- [ ] Real device integration
- [ ] Mobile app (React Native)
- [ ] Advanced reporting
- [ ] 10+ schools onboarded

### Q4 2024
- [ ] Fee management module
- [ ] Academic performance tracking
- [ ] Parent portal
- [ ] Government reporting integration
- [ ] 50+ schools target

---

**Built with ❤️ for Kenyan Schools**
