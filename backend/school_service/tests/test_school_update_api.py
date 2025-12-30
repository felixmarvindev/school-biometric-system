"""
Tests for School Update API endpoint (PUT /api/v1/schools/me).

Tests cover:
- Successful updates
- Authentication requirements
- Authorization (user can only update their own school)
- Validation errors
- School code immutability
- Not found scenarios
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from school_service.core.security import create_access_token, hash_password


# ==================== Fixtures ====================

@pytest.fixture
async def test_school(test_db: AsyncSession) -> School:
    """Create a test school in the database."""
    from school_service.models.school import School
    
    school = School(
        name="Test School",
        code="TEST-001",
        address="123 Test Street",
        phone="+254712345678",
        email="test@school.edu",
        is_deleted=False,
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    return school


@pytest.fixture
async def test_user(test_db: AsyncSession, test_school: School) -> User:
    """Create a test user with hashed password."""
    from school_service.models.user import User
    user = User(
        email="admin@test.edu",
        first_name="Test",
        last_name="Admin",
        hashed_password=hash_password("TestPassword123!"),
        school_id=test_school.id,
        role="school_admin",
        is_active=True,
        is_deleted=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate JWT token for test user."""
    return create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "first_name": test_user.first_name,
            "last_name": test_user.last_name,
            "school_id": test_user.school_id,
            "role": test_user.role,
        }
    )


@pytest.fixture
async def authenticated_client(
    client: AsyncClient, test_user: User, test_db: AsyncSession
) -> AsyncClient:
    """Create an authenticated test client."""
    from school_service.api.routes.auth import get_current_user
    from school_service.core.database import get_db
    from shared.schemas.user import UserResponse
    
    # Override dependencies
    async def override_get_current_user():
        return UserResponse.model_validate(test_user)
    
    async def override_get_db():
        yield test_db
    
    from school_service.main import app
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    
    return client


# ==================== Success Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_success(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test successful update of school information.
    
    Acceptance Criteria:
    - Returns 200 with updated school data
    - All updatable fields can be changed
    - Response includes both school and user information
    """
    update_data = {
        "name": "Updated School Name",
        "address": "456 New Address",
        "phone": "+254798765432",
        "email": "updated@school.edu",
    }
    
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify school data was updated
    assert data["name"] == update_data["name"]
    assert data["address"] == update_data["address"]
    assert data["phone"] == update_data["phone"]
    assert data["email"] == update_data["email"]
    
    # Verify school code is unchanged (immutable)
    assert data["code"] == test_school.code
    
    # Verify response includes user information
    assert "user" in data
    assert data["user"]["id"] is not None
    assert data["user"]["email"] is not None


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_partial(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test partial update (only some fields).
    
    Acceptance Criteria:
    - Can update only specific fields
    - Other fields remain unchanged
    """
    update_data = {
        "name": "Partially Updated Name",
    }
    
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify updated field
    assert data["name"] == update_data["name"]
    
    # Verify other fields remain unchanged
    assert data["code"] == test_school.code
    assert data["address"] == test_school.address
    assert data["phone"] == test_school.phone
    assert data["email"] == test_school.email


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_empty_fields(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test that optional fields can be cleared (set to null).
    
    Acceptance Criteria:
    - Optional fields can be set to null
    - Required fields (name, code) cannot be null
    """
    update_data = {
        "address": None,
        "phone": None,
        "email": None,
    }
    
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify optional fields can be null
    assert data["address"] is None
    assert data["phone"] is None
    assert data["email"] is None
    
    # Verify required fields remain
    assert data["name"] == test_school.name
    assert data["code"] == test_school.code


# ==================== Authentication Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_without_token(client: AsyncClient):
    """
    Test that endpoint requires authentication.
    
    Acceptance Criteria:
    - Returns 401 when no token provided
    """
    update_data = {"name": "Unauthorized Update"}
    
    response = await client.put("/api/v1/schools/me", json=update_data)
    
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_with_invalid_token(client: AsyncClient):
    """
    Test that endpoint rejects invalid tokens.
    
    Acceptance Criteria:
    - Returns 401 with invalid token
    """
    update_data = {"name": "Invalid Token Update"}
    
    response = await client.put(
        "/api/v1/schools/me",
        json=update_data,
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_with_expired_token(
    client: AsyncClient, test_user: User
):
    """
    Test that endpoint rejects expired tokens.
    
    Acceptance Criteria:
    - Returns 401 with expired token
    """
    from datetime import timedelta
    
    # Create expired token
    expired_token = create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "first_name": test_user.first_name,
            "last_name": test_user.last_name,
            "school_id": test_user.school_id,
            "role": test_user.role,
        },
        expires_delta=timedelta(seconds=-1),  # Already expired
    )
    
    update_data = {"name": "Expired Token Update"}
    
    response = await client.put(
        "/api/v1/schools/me",
        json=update_data,
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data


# ==================== Validation Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_invalid_name(
    authenticated_client: AsyncClient,
):
    """
    Test validation error for invalid name.
    
    Acceptance Criteria:
    - Returns 422 for name that's too short or too long
    """
    # Name too short
    update_data = {"name": ""}
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    assert response.status_code == 422
    
    # Name too long (over 200 characters)
    update_data = {"name": "a" * 201}
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_invalid_phone(
    authenticated_client: AsyncClient,
):
    """
    Test validation error for invalid phone format.
    
    Acceptance Criteria:
    - Returns 422 for invalid phone format
    """
    # Invalid phone format
    update_data = {"phone": "123"}  # Too short
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    assert response.status_code == 422
    
    # Invalid phone format (contains letters)
    update_data = {"phone": "+254-712-345-678"}
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_invalid_email(
    authenticated_client: AsyncClient,
):
    """
    Test validation error for invalid email format.
    
    Acceptance Criteria:
    - Returns 422 for invalid email format
    """
    update_data = {"email": "not-an-email"}
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_address_too_long(
    authenticated_client: AsyncClient,
):
    """
    Test validation error for address that's too long.
    
    Acceptance Criteria:
    - Returns 422 for address over 500 characters
    """
    update_data = {"address": "a" * 501}
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    assert response.status_code == 422


# ==================== Immutability Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_code_ignored(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test that school code cannot be updated (even if provided, it's ignored).
    
    Acceptance Criteria:
    - School code remains unchanged even if provided in update data
    - No error is raised (code is simply ignored)
    """
    original_code = test_school.code
    update_data = {
        "name": "Updated Name",
        "code": "NEW-CODE-123",  # Attempt to change code
    }
    
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify code is unchanged (immutable)
    assert data["code"] == original_code
    assert data["code"] != "NEW-CODE-123"
    
    # Verify name was updated
    assert data["name"] == "Updated Name"


# ==================== Not Found Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_not_found(
    authenticated_client: AsyncClient, test_db: AsyncSession, test_user: User
):
    """
    Test that endpoint returns 404 when school doesn't exist.
    
    Acceptance Criteria:
    - Returns 404 if school not found
    """
    # Delete the school
    from school_service.models.school import School
    school = await test_db.get(School, test_user.school_id)
    if school:
        school.is_deleted = True
        await test_db.commit()
    
    update_data = {"name": "Updated Name"}
    response = await authenticated_client.put("/api/v1/schools/me", json=update_data)
    
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()


# ==================== Authorization Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_authorization(
    client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
    test_user: User,
):
    """
    Test that user can only update their own school.
    
    Acceptance Criteria:
    - User can only update school associated with their school_id
    - Authorization is automatic via school_id from token
    """
    # Create another school
    other_school = School(
        name="Other School",
        code="OTHER-001",
        is_deleted=False,
    )
    test_db.add(other_school)
    await test_db.commit()
    await test_db.refresh(other_school)
    
    # User's school_id is test_school.id, not other_school.id
    # So they should only be able to update test_school
    update_data = {"name": "Updated Name"}
    
    # Create authenticated client for test_user (who belongs to test_school)
    from school_service.api.routes.auth import get_current_user
    from school_service.core.database import get_db
    from shared.schemas.user import UserResponse
    
    async def override_get_current_user():
        return UserResponse.model_validate(test_user)
    
    async def override_get_db():
        yield test_db
    
    from school_service.main import app
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    
    response = await client.put("/api/v1/schools/me", json=update_data)
    
    # Should succeed and update test_school (user's school)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_school.id
    assert data["name"] == "Updated Name"
    
    # Verify other_school was not affected
    from school_service.repositories.school_repository import SchoolRepository
    repo = SchoolRepository(test_db)
    other_school_after = await repo.get_by_id(other_school.id)
    assert other_school_after.name == "Other School"  # Unchanged


# ==================== API Documentation Tests ====================


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_school_api_documented(client: AsyncClient):
    """
    Test that the endpoint is properly documented in OpenAPI schema.
    
    Acceptance Criteria:
    - Endpoint appears in OpenAPI docs
    - Request/response schemas are documented
    """
    response = await client.get("/docs")
    assert response.status_code == 200
    
    # Check OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})
    
    # Verify endpoint exists
    assert "/api/v1/schools/me" in paths
    endpoint = paths["/api/v1/schools/me"]
    
    # Verify PUT method exists
    assert "put" in endpoint
    
    # Verify response model
    put_method = endpoint["put"]
    assert "responses" in put_method
    assert "200" in put_method["responses"]
    
    # Verify request body schema
    assert "requestBody" in put_method
    request_body = put_method["requestBody"]
    assert "content" in request_body
    assert "application/json" in request_body["content"]

