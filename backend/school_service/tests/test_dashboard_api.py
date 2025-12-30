"""Tests for Dashboard API (Task 006)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from school_service.core.security import hash_password, create_access_token
from shared.schemas.user import UserResponse


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
def auth_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    return create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "school_id": test_user.school_id,
            "role": test_user.role,
        }
    )


@pytest.fixture
async def authenticated_client(
    client: AsyncClient, test_user: User, test_db: AsyncSession
) -> AsyncClient:
    """
    Create an authenticated test client.
    
    Overrides get_current_user dependency to return the test user.
    """
    from school_service.main import app
    from school_service.api.routes.auth import get_current_user

    async def override_get_current_user():
        """Override get_current_user to return test user."""
        return UserResponse.model_validate(test_user)

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield client

    # Clean up
    if get_current_user in app.dependency_overrides:
        app.dependency_overrides.pop(get_current_user)


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_success(
    authenticated_client: AsyncClient, test_school: School, test_user: User
):
    """
    Test successful retrieval of current user's school.
    
    Acceptance Criteria:
    - GET `/api/v1/schools/me` endpoint exists
    - Endpoint requires authentication (JWT token)
    - Endpoint returns current user's school data
    - Response includes school information
    """
    response = await authenticated_client.get("/api/v1/schools/me")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure includes school
    assert "id" in data
    assert data["id"] == test_school.id
    assert data["name"] == test_school.name
    assert data["code"] == test_school.code
    assert data["address"] == test_school.address
    assert data["phone"] == test_school.phone
    assert data["email"] == test_school.email
    assert data["is_deleted"] is False
    assert "created_at" in data
    assert "updated_at" in data
    
    # Verify response includes user information
    assert "user" in data
    user_data = data["user"]
    assert user_data["id"] == test_user.id
    assert user_data["email"] == test_user.email
    assert user_data["first_name"] == test_user.first_name
    assert user_data["last_name"] == test_user.last_name
    assert user_data["school_id"] == test_user.school_id
    assert user_data["role"] == test_user.role


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_without_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when no token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    response = await client.get("/api/v1/schools/me")

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "credentials" in error_data["detail"].lower() or "not authenticated" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_with_invalid_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when invalid token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    headers = {"Authorization": "Bearer invalid_token_12345"}
    response = await client.get("/api/v1/schools/me", headers=headers)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "credentials" in error_data["detail"].lower() or "not authenticated" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_with_expired_token(client: AsyncClient, test_user: User):
    """
    Test that endpoint returns 401 when expired token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    from datetime import timedelta

    # Create an expired token (negative expiration)
    expired_token = create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "school_id": test_user.school_id,
            "role": test_user.role,
        },
        expires_delta=timedelta(minutes=-1),  # Expired 1 minute ago
    )

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/v1/schools/me", headers=headers)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_not_found(
    authenticated_client: AsyncClient, test_user: User, test_db: AsyncSession
):
    """
    Test that endpoint returns 404 when school doesn't exist.
    
    Acceptance Criteria:
    - Returns 404 if school not found
    """
    # Delete the school
    school = await test_db.get(School, test_user.school_id)
    if school:
        await test_db.delete(school)
        await test_db.commit()

    response = await authenticated_client.get("/api/v1/schools/me")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_deleted(
    authenticated_client: AsyncClient, test_school: School, test_db: AsyncSession
):
    """
    Test that endpoint returns 404 when school is soft-deleted.
    
    Acceptance Criteria:
    - Returns 404 if school not found (including soft-deleted)
    """
    # Soft delete the school
    test_school.is_deleted = True
    await test_db.commit()

    response = await authenticated_client.get("/api/v1/schools/me")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_authorization(
    client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
    test_user: User,
):
    """
    Test that user can only access their own school.
    
    Acceptance Criteria:
    - Authorization ensures user can only see their school
    """
    # Create a second school and user
    school2 = School(
        name="Another School",
        code="AS-001",
        address="Mombasa, Kenya",
        phone="+254798765432",
        email="admin@another.ac.ke",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    user2 = User(
        school_id=school2.id,
        email="admin2@another.ac.ke",
        hashed_password=hash_password("TestPassword123!"),
        first_name="Jane",
        last_name="Smith",
        role="school_admin",
        is_active=True,
        is_deleted=False,
    )
    test_db.add(user2)
    await test_db.commit()
    await test_db.refresh(user2)

    # Override get_current_user to return user2
    from school_service.main import app
    from school_service.api.routes.auth import get_current_user

    async def override_get_current_user():
        return UserResponse.model_validate(user2)

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        # User2 should get their own school (school2), not school1
        response = await client.get("/api/v1/schools/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == school2.id
        assert data["name"] == school2.name
        assert data["code"] == school2.code
        assert data["id"] != test_school.id  # Should not be test_school
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_api_documented(client: AsyncClient):
    """
    Test that API endpoint is documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoint is documented
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()

    # Check that the endpoint exists in the schema
    paths = schema.get("paths", {})
    assert "/api/v1/schools/me" in paths

    # Check that GET method exists
    endpoint = paths["/api/v1/schools/me"]
    assert "get" in endpoint

    # Check response schemas
    get_spec = endpoint["get"]
    assert "responses" in get_spec
    assert "200" in get_spec["responses"]  # Success response
    assert "401" in get_spec["responses"]  # Unauthorized response
    assert "404" in get_spec["responses"]  # Not found response

    # Check that endpoint requires authentication
    assert "security" in get_spec or "securitySchemes" in schema.get("components", {})


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_my_school_inactive_user(
    client: AsyncClient, test_user: User, test_db: AsyncSession
):
    """
    Test that inactive users cannot access the endpoint.
    
    Acceptance Criteria:
    - Returns 403 if user account is inactive
    """
    # Deactivate the user
    test_user.is_active = False
    await test_db.commit()

    # Create token for inactive user
    token = create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "school_id": test_user.school_id,
            "role": test_user.role,
        }
    )

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/schools/me", headers=headers)

    # Should return 403 (Forbidden) because user is inactive
    # Note: This depends on get_current_user checking is_active
    assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data

