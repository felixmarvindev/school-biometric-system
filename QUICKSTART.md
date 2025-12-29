# Developer Quick Start Guide

Get up and running with the School Biometric Management System in under 30 minutes.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Python 3.11+** installed (`python --version`)
- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **Docker Desktop** installed and running (`docker --version`)
- [ ] **Git** configured (`git --version`)
- [ ] **Code editor** (VS Code recommended)
- [ ] **Terminal** (bash/zsh for Mac/Linux, WSL for Windows)

## Step 1: Clone and Setup (5 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd school-biometric-system

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

### Configure Environment Variables

#### Backend `.env`
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/school_biometric

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
SIMULATION_MODE=true  # Set to true for development without devices

# SMS (Use sandbox for development)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-sandbox-api-key
AFRICASTALKING_SENDER_ID=SchoolBio

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

#### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=School Biometric System
```

## Step 2: Start Infrastructure (2 minutes)

```bash
# Start PostgreSQL, Redis, and PgAdmin
docker-compose up -d

# Verify services are running
docker ps
```

You should see:
- `postgres` on port 5432
- `redis` on port 6379
- `pgadmin` on port 5050 (optional, for database management)

### Verify Database Connection

```bash
# Test PostgreSQL connection
docker exec -it school-biometric-postgres psql -U postgres -d school_biometric

# Inside psql, run:
\l  # List databases
\q  # Quit
```

## Step 3: Backend Setup (10 minutes)

### Create Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# This installs:
# - FastAPI
# - SQLAlchemy
# - Alembic
# - Pydantic
# - python-socketio
# - And more...
```

### Database Migrations

```bash
# Initialize Alembic (only first time)
# Already done if project is set up, skip this
# alembic init alembic

# Run migrations to create tables
alembic upgrade head

# You should see: "Running upgrade -> xxx, initial schema"
```

### Verify Database Schema

```bash
# Connect to database
docker exec -it school-biometric-postgres psql -U postgres -d school_biometric

# List tables
\dt

# You should see:
# schools, students, classes, streams, devices, 
# enrollments, attendance_records, notifications, etc.
```

## Step 4: Start Backend Services (3 minutes)

Open **separate terminal windows/tabs** for each service:

### Terminal 1: API Gateway
```bash
cd backend/api_gateway
source ../venv/bin/activate  # Activate venv
uvicorn main:app --reload --port 8000

# You should see:
# INFO: Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: School Service
```bash
cd backend/school_service
source ../venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Terminal 3: Device Service
```bash
cd backend/device_service
source ../venv/bin/activate
uvicorn main:app --reload --port 8002
```

### Terminal 4: Attendance Service
```bash
cd backend/attendance_service
source ../venv/bin/activate
uvicorn main:app --reload --port 8003
```

### Terminal 5: Notification Service
```bash
cd backend/notification_service
source ../venv/bin/activate
uvicorn main:app --reload --port 8004
```

### Verify Services Are Running

```bash
# Check API Gateway
curl http://localhost:8000/health

# Check all services
curl http://localhost:8001/health  # School Service
curl http://localhost:8002/health  # Device Service
curl http://localhost:8003/health  # Attendance Service
curl http://localhost:8004/health  # Notification Service
```

### View API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 5: Frontend Setup (5 minutes)

### New Terminal: Frontend

```bash
cd frontend

# Install dependencies
npm install

# This installs:
# - Next.js
# - React
# - Tailwind CSS
# - shadcn/ui components
# - Socket.IO client
# - And more...
```

### Start Development Server

```bash
npm run dev

# You should see:
# ▲ Next.js 14.x.x
# - Local: http://localhost:3000
# - Ready in Xms
```

Open browser: **http://localhost:3000**

## Step 6: Create Sample Data (5 minutes)

### Using the API

```bash
# Create a school
curl -X POST http://localhost:8000/api/v1/schools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Greenfield Academy",
    "code": "GFA2024",
    "address": "123 Education Lane, Nairobi",
    "phone": "+254712345678",
    "email": "admin@greenfield.ac.ke"
  }'

# Response will include the school_id, use it below

# Create an admin user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@greenfield.ac.ke",
    "password": "Admin123!",
    "first_name": "John",
    "last_name": "Kamau",
    "school_id": 1,
    "role": "school_admin"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@greenfield.ac.ke",
    "password": "Admin123!"
  }'

# Save the access_token from the response
```

### Or Use the Seed Script

```bash
cd backend
python scripts/seed_data.py

# This creates:
# - 1 school
# - 1 admin user
# - 3 classes with streams
# - 50 sample students
# - 2 devices
# - Sample enrollments
```

## Step 7: Test the System (5 minutes)

### Test Enrollment (Simulated)

```bash
# Start enrollment for student ID 1 on device ID 1
curl -X POST http://localhost:8000/api/v1/enrollment/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "student_id": 1,
    "device_id": 1,
    "finger_id": 0
  }'

# Watch the WebSocket events in browser console
# Or use a WebSocket client to monitor events
```

### Test Attendance Event

```bash
# Simulate an attendance event
curl -X POST http://localhost:8000/api/v1/attendance/simulate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "student_id": 1,
    "device_id": 1,
    "event_type": "IN"
  }'

# Check if SMS was sent (in sandbox mode, check logs)
```

## Common Development Tasks

### Running Tests

```bash
# Backend tests
cd backend/school_service
pytest tests/ -v

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

### Database Management

```bash
# Create a new migration
cd backend
alembic revision -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Reset Database

```bash
# Drop all tables and recreate
alembic downgrade base
alembic upgrade head

# Re-seed data
python scripts/seed_data.py
```

### View Logs

```bash
# Docker services
docker-compose logs -f postgres
docker-compose logs -f redis

# Application logs (in each service terminal)
# Logs appear in real-time

# Or configure logging to file
# Check logs/ directory in each service
```

### Code Formatting

```bash
# Backend (Python)
cd backend
black .
isort .
mypy .

# Frontend (TypeScript)
cd frontend
npm run lint
npm run format
```

## Development Workflow

### Daily Routine

```bash
# 1. Pull latest changes
git pull origin main

# 2. Start infrastructure
docker-compose up -d

# 3. Activate backend venv
cd backend
source venv/bin/activate

# 4. Start all services (in separate terminals)
# API Gateway, School Service, Device Service, etc.

# 5. Start frontend (new terminal)
cd frontend
npm run dev

# 6. Start coding!
```

### Before Committing

```bash
# 1. Run tests
cd backend && pytest tests/ && cd ../frontend && npm run test

# 2. Format code
cd backend && black . && isort . && cd ../frontend && npm run format

# 3. Check types
cd backend && mypy . && cd ../frontend && npm run type-check

# 4. Commit with good message
git add .
git commit -m "feat(enrollment): add bulk enrollment support"
git push
```

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Database Connection Failed

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check connection string in .env
echo $DATABASE_URL
```

### Issue: Redis Connection Failed

```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
docker exec -it school-biometric-redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

### Issue: Module Not Found (Python)

```bash
# Make sure venv is activated
which python  # Should show path to venv

# Reinstall requirements
pip install -r requirements.txt

# If still fails, recreate venv
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Module Not Found (Node.js)

```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Issue: Alembic Migration Fails

```bash
# Check current migration state
alembic current

# View migration history
alembic history

# Force to specific revision
alembic stamp head

# Or reset completely
alembic downgrade base
alembic upgrade head
```

### Issue: WebSocket Not Connecting

```bash
# Check CORS settings in backend
# Ensure frontend URL is in ALLOWED_ORIGINS

# Check browser console for errors
# Look for CORS or connection refused errors

# Verify Socket.IO server is running
curl http://localhost:8000/socket.io/
```

## Useful Commands

### Docker

```bash
# View all containers
docker ps -a

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]

# Stop all services
docker-compose down

# Remove volumes (CAUTION: deletes data)
docker-compose down -v

# Rebuild a service
docker-compose up -d --build [service_name]
```

### Database

```bash
# Enter PostgreSQL shell
docker exec -it school-biometric-postgres psql -U postgres -d school_biometric

# Useful psql commands:
\l              # List databases
\dt             # List tables
\d [table]      # Describe table
\q              # Quit

# Backup database
docker exec school-biometric-postgres pg_dump -U postgres school_biometric > backup.sql

# Restore database
docker exec -i school-biometric-postgres psql -U postgres school_biometric < backup.sql
```

### Git

```bash
# Create feature branch
git checkout -b feature/my-feature

# View changed files
git status

# Stage specific files
git add path/to/file

# Commit with message
git commit -m "type(scope): message"

# Push to remote
git push origin feature/my-feature

# Pull latest changes
git pull origin main

# Merge main into your branch
git merge main
```

## Next Steps

Now that you're set up:

1. **Read the docs**:
   - [README.md](./README.md) - Project overview
   - [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical details
   - [.cursor_project_rules](./.cursor_project_rules) - Coding standards

2. **Explore the codebase**:
   - Study the service structure
   - Understand the data models
   - Review the API endpoints

3. **Pick a task**:
   - Check the issue tracker
   - Start with a "good first issue"
   - Ask questions in Slack/Discord

4. **Write your first feature**:
   - Follow the architecture patterns
   - Write tests
   - Submit a PR

## Getting Help

- 📚 **Documentation**: Check README.md and ARCHITECTURE.md
- 💬 **Team Chat**: [Slack/Discord channel]
- 🐛 **Bug Reports**: [GitHub Issues]
- 📧 **Email**: dev-team@yourcompany.com
- 📅 **Office Hours**: Tuesday/Thursday 2-4 PM EAT

## Keyboard Shortcuts (VS Code)

```
Ctrl/Cmd + P          → Quick file search
Ctrl/Cmd + Shift + P  → Command palette
Ctrl/Cmd + `          → Toggle terminal
Ctrl/Cmd + B          → Toggle sidebar
F12                   → Go to definition
Alt + Click           → Add cursor
Ctrl/Cmd + D          → Select next occurrence
Ctrl/Cmd + /          → Toggle comment
```

---

**Welcome to the team! 🎉**

If you encounter any issues not covered here, please update this guide and submit a PR.
