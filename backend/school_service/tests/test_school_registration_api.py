"""Tests for School Registration API (Task 002)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_success(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test successful school registration.
    
    Acceptance Criteria:
    - POST `/api/v1/schools/register` endpoint exists
    - Endpoint accepts school registration data
    - Successful registration returns 201 with school data
    """
    response = await client.post("/api/v1/schools/register", json=valid_school_data)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify response structure
    assert "id" in data
    assert data["name"] == valid_school_data["name"]
    assert data["code"] == valid_school_data["code"].upper()  # Code should be uppercase
    assert data["address"] == valid_school_data["address"]
    assert data["phone"] == valid_school_data["phone"]
    assert data["email"] == valid_school_data["email"]
    assert "created_at" in data
    assert "is_deleted" in data
    assert data["is_deleted"] is False
    
    # Verify admin_user is included in response
    assert "admin_user" in data
    admin_user = data["admin_user"]
    assert admin_user["email"] == valid_school_data["admin"]["email"]
    assert admin_user["first_name"] == valid_school_data["admin"]["first_name"]
    assert admin_user["last_name"] == valid_school_data["admin"]["last_name"]
    assert "password" not in admin_user  # Password should not be in response


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_minimal_data(
    client: AsyncClient, minimal_school_data: dict, test_db: AsyncSession
):
    """
    Test school registration with minimal required fields only.
    
    Acceptance Criteria:
    - Endpoint accepts school registration data
    - Optional fields can be omitted
    """
    response = await client.post("/api/v1/schools/register", json=minimal_school_data)

    assert response.status_code == 201
    data = response.json()
    
    assert data["name"] == minimal_school_data["name"]
    assert data["code"] == minimal_school_data["code"].upper()
    assert data["address"] is None
    assert data["phone"] is None
    assert data["email"] is None
    
    # Verify admin_user is included in response
    assert "admin_user" in data
    admin_user = data["admin_user"]
    assert admin_user["email"] == minimal_school_data["admin"]["email"]
    assert admin_user["first_name"] == minimal_school_data["admin"]["first_name"]
    assert admin_user["last_name"] == minimal_school_data["admin"]["last_name"]


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_duplicate_code(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test duplicate school code validation.
    
    Acceptance Criteria:
    - School code uniqueness is validated
    - Duplicate code returns 409 with specific error
    """
    # Register first school
    response1 = await client.post("/api/v1/schools/register", json=valid_school_data)
    assert response1.status_code == 201

    # Try to register with same code (different case)
    # Need to change admin email too since it must be unique
    duplicate_data = valid_school_data.copy()
    duplicate_data["code"] = valid_school_data["code"].lower()  # Different case
    duplicate_data["admin"] = valid_school_data["admin"].copy()
    duplicate_data["admin"]["email"] = "admin2@greenfield.ac.ke"  # Different email
    
    response2 = await client.post("/api/v1/schools/register", json=duplicate_data)
    
    assert response2.status_code == 409
    error_data = response2.json()
    assert "detail" in error_data
    assert "already exists" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_missing_name(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for missing required field (name).
    
    Acceptance Criteria:
    - Input validation works (required fields)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    del invalid_data["name"]
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_missing_code(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for missing required field (code).
    
    Acceptance Criteria:
    - Input validation works (required fields)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    del invalid_data["code"]
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_missing_admin(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for missing required field (admin).
    
    Acceptance Criteria:
    - Input validation works (required fields)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    del invalid_data["admin"]
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_invalid_email_format(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for invalid email format.
    
    Acceptance Criteria:
    - Input validation works (formats)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    invalid_data["email"] = "not-a-valid-email"
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_invalid_phone_format(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for invalid phone format.
    
    Acceptance Criteria:
    - Input validation works (formats)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    invalid_data["phone"] = "123"  # Too short
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_invalid_code_format(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for invalid school code format.
    
    Acceptance Criteria:
    - Input validation works (formats)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    invalid_data["code"] = "invalid code!"  # Contains invalid characters
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_name_too_long(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test validation error for name exceeding max length.
    
    Acceptance Criteria:
    - Input validation works (formats)
    - Validation errors return 422 with clear messages
    """
    invalid_data = valid_school_data.copy()
    invalid_data["name"] = "A" * 201  # Exceeds max length of 200
    
    response = await client.post("/api/v1/schools/register", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_code_normalized_to_uppercase(
    client: AsyncClient, valid_school_data: dict, test_db: AsyncSession
):
    """
    Test that school code is normalized to uppercase.
    
    Acceptance Criteria:
    - School code is automatically converted to uppercase
    """
    data = valid_school_data.copy()
    data["code"] = "gfa-001"  # Lowercase
    
    response = await client.post("/api/v1/schools/register", json=data)
    
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["code"] == "GFA-001"  # Should be uppercase


@pytest.mark.asyncio
@pytest.mark.api
async def test_register_school_api_documented(client: AsyncClient):
    """
    Test that API endpoint is documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoint is documented (OpenAPI)
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    
    # Check that the endpoint exists in the schema
    paths = schema.get("paths", {})
    assert "/api/v1/schools/register" in paths
    
    # Check that POST method exists
    endpoint = paths["/api/v1/schools/register"]
    assert "post" in endpoint
    
    # Check response schemas
    post_spec = endpoint["post"]
    assert "responses" in post_spec
    assert "201" in post_spec["responses"]  # Success response
    assert "409" in post_spec["responses"]  # Conflict response
    assert "422" in post_spec["responses"]  # Validation error response

