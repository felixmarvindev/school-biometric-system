"""Tests for Authentication Login API (Task 011)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from school_service.core.security import hash_password, create_access_token, decode_access_token
from school_service.services.user_service import UserService
from shared.schemas.user import UserCreate


@pytest.fixture
async def test_school(test_db: AsyncSession) -> School:
    """Create a test school in the database."""
    school = School(
        name="Greenfield Academy",
        code="GFA-001",
        address="Nairobi, Kenya",
        phone="+254712345678",
        email="admin@greenfield.ac.ke",
        is_deleted=False,
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    return school


@pytest.fixture
async def test_user(test_db: AsyncSession, test_school: School) -> User:
    """Create a test user in the database."""
    user = User(
        school_id=test_school.id,
        email="admin@greenfield.ac.ke",
        hashed_password=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        role="school_admin",
        is_active=True,
        is_deleted=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def inactive_user(test_db: AsyncSession, test_school: School) -> User:
    """Create an inactive test user in the database."""
    user = User(
        school_id=test_school.id,
        email="inactive@greenfield.ac.ke",
        hashed_password=hash_password("TestPassword123!"),
        first_name="Inactive",
        last_name="User",
        role="school_admin",
        is_active=False,  # Inactive
        is_deleted=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


# ==================== JSON Login Endpoint Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_success(
    client: AsyncClient, test_user: User
):
    """
    Test successful login with JSON endpoint.
    
    Acceptance Criteria:
    - POST `/api/v1/auth/login/json` endpoint exists
    - Login API call works
    - Returns JWT token on success
    """
    login_data = {
        "email": test_user.email,
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    
    # Verify token is valid and contains expected claims
    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == str(test_user.id)
    assert payload.get("email") == test_user.email
    assert payload.get("school_id") == test_user.school_id
    assert payload.get("role") == test_user.role


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_invalid_email(client: AsyncClient):
    """
    Test login with invalid email.
    
    Acceptance Criteria:
    - Error messages displayed for invalid credentials
    - Returns 401 for invalid email
    """
    login_data = {
        "email": "nonexistent@example.com",
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data
    assert "incorrect" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_invalid_password(
    client: AsyncClient, test_user: User
):
    """
    Test login with invalid password.
    
    Acceptance Criteria:
    - Error messages displayed for invalid credentials
    - Returns 401 for invalid password
    """
    login_data = {
        "email": test_user.email,
        "password": "WrongPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data
    assert "incorrect" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_inactive_user(
    client: AsyncClient, inactive_user: User
):
    """
    Test login with inactive user account.
    
    Acceptance Criteria:
    - Returns 401 for inactive user
    """
    login_data = {
        "email": inactive_user.email,
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_missing_email(client: AsyncClient):
    """
    Test login with missing email field.
    
    Acceptance Criteria:
    - Form validation works
    - Returns 422 for missing required field
    """
    login_data = {
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_missing_password(client: AsyncClient):
    """
    Test login with missing password field.
    
    Acceptance Criteria:
    - Form validation works
    - Returns 422 for missing required field
    """
    login_data = {
        "email": "admin@greenfield.ac.ke",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_invalid_email_format(client: AsyncClient):
    """
    Test login with invalid email format.
    
    Acceptance Criteria:
    - Form validation works
    - Returns 422 for invalid email format
    """
    login_data = {
        "email": "not-a-valid-email",
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_case_insensitive_email(
    client: AsyncClient, test_user: User
):
    """
    Test that email is case-insensitive for login.
    
    Acceptance Criteria:
    - Email matching is case-insensitive
    """
    login_data = {
        "email": test_user.email.upper(),  # Uppercase email
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "access_token" in data


# ==================== Form Login Endpoint Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_form_success(
    client: AsyncClient, test_user: User
):
    """
    Test successful login with form endpoint.
    
    Acceptance Criteria:
    - POST `/api/v1/auth/login` endpoint exists
    - Login API call works with form data
    - Returns JWT token on success
    """
    # OAuth2PasswordRequestForm uses 'username' for email
    form_data = {
        "username": test_user.email,
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login", data=form_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    
    # Verify token is valid
    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == str(test_user.id)


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_form_invalid_credentials(client: AsyncClient):
    """
    Test login form with invalid credentials.
    
    Acceptance Criteria:
    - Returns 401 for invalid credentials
    """
    form_data = {
        "username": "nonexistent@example.com",
        "password": "WrongPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login", data=form_data)
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data
    assert "incorrect" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_form_missing_fields(client: AsyncClient):
    """
    Test login form with missing fields.
    
    Acceptance Criteria:
    - Returns 422 for missing required fields
    """
    # Missing password
    form_data = {
        "username": "admin@greenfield.ac.ke",
    }
    
    response = await client.post("/api/v1/auth/login", data=form_data)
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data


# ==================== Token Validation Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_token_contains_user_info(
    client: AsyncClient, test_user: User, test_school: School
):
    """
    Test that JWT token contains all necessary user information.
    
    Acceptance Criteria:
    - Token contains user ID, email, first_name, last_name, school_id, and role
    - Token is the source of truth for user information
    """
    login_data = {
        "email": test_user.email,
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 200
    
    data = response.json()
    token = data["access_token"]
    payload = decode_access_token(token)
    
    assert payload is not None
    assert payload.get("sub") == str(test_user.id)
    assert payload.get("email") == test_user.email
    assert payload.get("first_name") == test_user.first_name
    assert payload.get("last_name") == test_user.last_name
    assert payload.get("school_id") == test_user.school_id
    assert payload.get("role") == test_user.role
    assert "exp" in payload  # Expiration time
    assert "iat" in payload  # Issued at time


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_token_expiration(
    client: AsyncClient, test_user: User
):
    """
    Test that JWT token has expiration time.
    
    Acceptance Criteria:
    - Token has expiration claim
    """
    login_data = {
        "email": test_user.email,
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    assert response.status_code == 200
    
    data = response.json()
    token = data["access_token"]
    payload = decode_access_token(token)
    
    assert payload is not None
    assert "exp" in payload
    assert payload["exp"] > 0  # Expiration should be in the future


# ==================== API Documentation Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_json_api_documented(client: AsyncClient):
    """
    Test that login JSON endpoint is documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoint is documented
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    
    # Check that the endpoint exists in the schema
    paths = schema.get("paths", {})
    assert "/api/v1/auth/login/json" in paths
    
    # Check that POST method exists
    endpoint = paths["/api/v1/auth/login/json"]
    assert "post" in endpoint
    
    # Check response schemas
    post_spec = endpoint["post"]
    assert "responses" in post_spec
    assert "200" in post_spec["responses"]  # Success response
    assert "401" in post_spec["responses"]  # Unauthorized response


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_form_api_documented(client: AsyncClient):
    """
    Test that login form endpoint is documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoint is documented
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    
    # Check that the endpoint exists in the schema
    paths = schema.get("paths", {})
    assert "/api/v1/auth/login" in paths
    
    # Check that POST method exists
    endpoint = paths["/api/v1/auth/login"]
    assert "post" in endpoint
    
    # Check response schemas
    post_spec = endpoint["post"]
    assert "responses" in post_spec
    assert "200" in post_spec["responses"]  # Success response
    assert "401" in post_spec["responses"]  # Unauthorized response


# ==================== Edge Cases ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_empty_request_body(client: AsyncClient):
    """
    Test login with empty request body.
    
    Acceptance Criteria:
    - Returns 422 for empty body
    """
    response = await client.post("/api/v1/auth/login/json", json={})
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
    
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_deleted_user(
    client: AsyncClient, test_db: AsyncSession, test_school: School
):
    """
    Test login with soft-deleted user.
    
    Acceptance Criteria:
    - Returns 401 for deleted user
    """
    # Create a deleted user
    deleted_user = User(
        school_id=test_school.id,
        email="deleted@greenfield.ac.ke",
        hashed_password=hash_password("TestPassword123!"),
        first_name="Deleted",
        last_name="User",
        role="school_admin",
        is_active=True,
        is_deleted=True,  # Soft-deleted
    )
    test_db.add(deleted_user)
    await test_db.commit()
    await test_db.refresh(deleted_user)
    
    login_data = {
        "email": deleted_user.email,
        "password": "TestPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login/json", json=login_data)
    
    # Should return 401 because user is deleted (authenticate_user checks is_active, not is_deleted)
    # But if the user is not found or inactive, it returns 401
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_login_both_endpoints_same_result(
    client: AsyncClient, test_user: User
):
    """
    Test that both login endpoints return the same token structure.
    
    Acceptance Criteria:
    - Both endpoints return consistent token format
    """
    # Login with JSON endpoint
    json_data = {
        "email": test_user.email,
        "password": "TestPassword123!",
    }
    json_response = await client.post("/api/v1/auth/login/json", json=json_data)
    
    # Login with form endpoint
    form_data = {
        "username": test_user.email,
        "password": "TestPassword123!",
    }
    form_response = await client.post("/api/v1/auth/login", data=form_data)
    
    # Both should succeed
    assert json_response.status_code == 200
    assert form_response.status_code == 200
    
    json_result = json_response.json()
    form_result = form_response.json()
    
    # Both should have the same structure
    assert "access_token" in json_result
    assert "access_token" in form_result
    assert "token_type" in json_result
    assert "token_type" in form_result
    assert json_result["token_type"] == form_result["token_type"] == "bearer"
    
    # Both tokens should decode to the same user ID
    json_token = json_result["access_token"]
    form_token = form_result["access_token"]
    
    json_payload = decode_access_token(json_token)
    form_payload = decode_access_token(form_token)
    
    assert json_payload is not None
    assert form_payload is not None
    assert json_payload.get("sub") == form_payload.get("sub") == str(test_user.id)

