# School Service Tests

## Overview

This directory contains tests for the School Service, specifically for Task 002: School Registration API.

## Running Tests

### Install Test Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests

```bash
cd backend
pytest school_service/tests/ -v
```

### Run Specific Test File

```bash
cd backend
pytest school_service/tests/test_school_registration_api.py -v
```

### Run Specific Test

```bash
cd backend
pytest school_service/tests/test_school_registration_api.py::test_register_school_success -v
```

### Run Tests with Coverage

```bash
cd backend
pytest school_service/tests/ --cov=school_service --cov-report=html --cov-report=term
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_school_registration_api.py` - Tests for School Registration API (Task 002)

## Test Database

Tests use an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) for fast execution. Each test gets a fresh database instance.

## Test Markers

Tests are marked with:
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.integration` - Integration tests (requires database)
- `@pytest.mark.unit` - Unit tests (fast, no database)

Run tests by marker:
```bash
pytest -m api
pytest -m integration
pytest -m unit
```

## Task 002 Test Coverage

The `test_school_registration_api.py` file covers all acceptance criteria for Task 002:

✅ POST `/api/v1/schools/register` endpoint exists  
✅ Endpoint accepts school registration data  
✅ Input validation works (required fields, formats)  
✅ School code uniqueness is validated  
✅ Successful registration returns 201 with school data  
✅ Validation errors return 422 with clear messages  
✅ Duplicate code returns 409 with specific error  
✅ API endpoint is documented (OpenAPI)  

