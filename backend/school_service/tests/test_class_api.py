"""Tests for Class API (Task 023)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from school_service.models.academic_class import AcademicClass
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
async def test_class(test_db: AsyncSession, test_school: School) -> AcademicClass:
    """Create a test class in the database."""
    academic_class = AcademicClass(
        school_id=test_school.id,
        name="Form 1",
        description="First form class",
        is_deleted=False,
    )
    test_db.add(academic_class)
    await test_db.commit()
    await test_db.refresh(academic_class)
    return academic_class


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
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


# ============================================================================
# Create Class API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_create_class_success(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test successful class creation.
    
    Acceptance Criteria:
    - POST `/api/v1/classes` endpoint exists
    - Returns 201 with created class data
    """
    class_data = {
        "name": "Form 2",
        "description": "Second form class",
    }

    response = await authenticated_client.post("/api/v1/classes", json=class_data)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert "id" in data
    assert data["name"] == class_data["name"]
    assert data["description"] == class_data["description"]
    assert data["school_id"] == test_school.id  # Should be auto-assigned
    assert data["is_deleted"] is False
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_class_without_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when no token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    class_data = {
        "name": "Form 3",
        "description": "Third form class",
    }

    response = await client.post("/api/v1/classes", json=class_data)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_class_duplicate_name(
    authenticated_client: AsyncClient, test_class: AcademicClass
):
    """
    Test that duplicate class name returns 409.
    
    Acceptance Criteria:
    - Returns 409 for duplicate class name
    """
    class_data = {
        "name": test_class.name,  # Duplicate
        "description": "Duplicate class",
    }

    response = await authenticated_client.post("/api/v1/classes", json=class_data)

    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "name" in error_data["detail"].lower() or "already exists" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_class_validation_errors(authenticated_client: AsyncClient):
    """
    Test that validation errors return 422.
    
    Acceptance Criteria:
    - Returns 422 for validation errors
    """
    # Missing required field
    class_data = {
        # Missing name
        "description": "Test class",
    }

    response = await authenticated_client.post("/api/v1/classes", json=class_data)

    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


# ============================================================================
# List Classes API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_list_classes_success(
    authenticated_client: AsyncClient, test_class: AcademicClass
):
    """
    Test successful class list retrieval.
    
    Acceptance Criteria:
    - GET `/api/v1/classes` endpoint exists
    - Returns list of classes
    """
    response = await authenticated_client.get("/api/v1/classes")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify class data structure
    class_item = data[0]
    assert "id" in class_item
    assert "name" in class_item
    assert "school_id" in class_item


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_classes_only_user_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
    test_user: User,
):
    """
    Test that only classes from user's school are returned.
    
    Acceptance Criteria:
    - Returns only classes from authenticated user's school
    """
    # Create another school and class
    school2 = School(
        name="Another School",
        code="AS-001",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    class2 = AcademicClass(
        school_id=school2.id,
        name="Form 1",
        is_deleted=False,
    )
    test_db.add(class2)
    await test_db.commit()

    # List classes - should only get test_school classes
    response = await authenticated_client.get("/api/v1/classes")

    assert response.status_code == 200
    data = response.json()

    # Verify no classes from school2 are returned
    for class_item in data:
        assert class_item["school_id"] == test_school.id
        assert class_item["school_id"] != school2.id


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_classes_excludes_deleted(
    authenticated_client: AsyncClient, test_db: AsyncSession, test_school: School
):
    """
    Test that soft-deleted classes are not returned.
    
    Acceptance Criteria:
    - Only active (non-deleted) classes returned by default
    """
    # Create a deleted class
    deleted_class = AcademicClass(
        school_id=test_school.id,
        name="Deleted Class",
        is_deleted=True,
    )
    test_db.add(deleted_class)
    await test_db.commit()

    # List classes - should not include deleted
    response = await authenticated_client.get("/api/v1/classes")

    assert response.status_code == 200
    data = response.json()

    # Verify deleted class is not in results
    deleted_ids = [c["id"] for c in data]
    assert deleted_class.id not in deleted_ids


# ============================================================================
# Get Class by ID API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_get_class_by_id_success(
    authenticated_client: AsyncClient, test_class: AcademicClass
):
    """
    Test successful class retrieval by ID.
    
    Acceptance Criteria:
    - GET `/api/v1/classes/{id}` endpoint exists
    - Returns 200 with class data
    """
    response = await authenticated_client.get(f"/api/v1/classes/{test_class.id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert data["id"] == test_class.id
    assert data["name"] == test_class.name
    assert data["school_id"] == test_class.school_id


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_class_by_id_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent class returns 404.
    
    Acceptance Criteria:
    - Returns 404 if class not found
    """
    response = await authenticated_client.get("/api/v1/classes/99999")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_class_by_id_different_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_user: User,
):
    """
    Test that class from different school returns 404.
    
    Acceptance Criteria:
    - Returns 404 if class belongs to different school
    """
    # Create another school and class
    school2 = School(
        name="Another School",
        code="AS-002",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    class2 = AcademicClass(
        school_id=school2.id,
        name="Form 1",
        is_deleted=False,
    )
    test_db.add(class2)
    await test_db.commit()
    await test_db.refresh(class2)

    # Try to get class from different school
    response = await authenticated_client.get(f"/api/v1/classes/{class2.id}")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "not found" in error_data["detail"].lower()


# ============================================================================
# Update Class API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_update_class_success(
    authenticated_client: AsyncClient, test_class: AcademicClass
):
    """
    Test successful class update.
    
    Acceptance Criteria:
    - PUT `/api/v1/classes/{id}` endpoint exists
    - Returns 200 with updated class data
    """
    update_data = {
        "name": "Form 1 Updated",
        "description": "Updated description",
    }

    response = await authenticated_client.put(
        f"/api/v1/classes/{test_class.id}", json=update_data
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify updated fields
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

    # Verify unchanged fields
    assert data["school_id"] == test_class.school_id


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_class_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent class returns 404.
    
    Acceptance Criteria:
    - Returns 404 if class not found
    """
    update_data = {"name": "Updated"}

    response = await authenticated_client.put("/api/v1/classes/99999", json=update_data)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_class_duplicate_name(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
):
    """
    Test that updating to duplicate name returns 409.
    
    Acceptance Criteria:
    - Returns 409 if new name already exists
    """
    # Create two classes
    class1 = AcademicClass(
        school_id=test_school.id,
        name="Form 1",
        is_deleted=False,
    )
    class2 = AcademicClass(
        school_id=test_school.id,
        name="Form 2",
        is_deleted=False,
    )
    test_db.add(class1)
    test_db.add(class2)
    await test_db.commit()
    await test_db.refresh(class1)
    await test_db.refresh(class2)

    # Try to update class2 to class1's name
    update_data = {"name": "Form 1"}

    response = await authenticated_client.put(f"/api/v1/classes/{class2.id}", json=update_data)

    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "name" in error_data["detail"].lower() or "already exists" in error_data["detail"].lower()


# ============================================================================
# Delete Class API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_class_success(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
):
    """
    Test successful class soft delete.
    
    Acceptance Criteria:
    - DELETE `/api/v1/classes/{id}` endpoint exists
    - Performs soft delete (sets is_deleted = true)
    - Returns 204 No Content on success
    """
    # Create a class to delete
    academic_class = AcademicClass(
        school_id=test_school.id,
        name="Form To Delete",
        is_deleted=False,
    )
    test_db.add(academic_class)
    await test_db.commit()
    await test_db.refresh(academic_class)

    response = await authenticated_client.delete(f"/api/v1/classes/{academic_class.id}")

    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    # Verify class is soft-deleted (still exists but marked as deleted)
    await test_db.refresh(academic_class)
    assert academic_class.is_deleted is True, "Class should be soft-deleted"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_class_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent class returns 404.
    
    Acceptance Criteria:
    - Returns 404 if class not found
    """
    response = await authenticated_client.delete("/api/v1/classes/99999")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_class_data_preserved(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
):
    """
    Test that class data is preserved after soft delete.
    
    Acceptance Criteria:
    - Class data is preserved (not hard deleted)
    """
    # Create a class
    academic_class = AcademicClass(
        school_id=test_school.id,
        name="Form Preserve",
        description="Preserve data",
        is_deleted=False,
    )
    test_db.add(academic_class)
    await test_db.commit()
    await test_db.refresh(academic_class)

    class_id = academic_class.id
    class_name = academic_class.name

    # Delete class
    response = await authenticated_client.delete(f"/api/v1/classes/{class_id}")
    assert response.status_code == 204

    # Verify class still exists in database (soft delete)
    class_check = await test_db.get(AcademicClass, class_id)
    assert class_check is not None, "Class should still exist in database"
    assert class_check.is_deleted is True, "Class should be marked as deleted"
    assert class_check.name == class_name, "Class data should be preserved"


# ============================================================================
# API Documentation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_class_api_documented(client: AsyncClient):
    """
    Test that all class API endpoints are documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoints are documented
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    paths = schema.get("paths", {})

    # Check all endpoints exist
    classes_path = "/api/v1/classes"
    classes_path_with_slash = "/api/v1/classes/"
    
    # Use whichever format FastAPI provides
    if classes_path in paths:
        endpoint_path = classes_path
    elif classes_path_with_slash in paths:
        endpoint_path = classes_path_with_slash
    else:
        pytest.fail(f"Expected '/api/v1/classes' or '/api/v1/classes/' in paths, got: {list(paths.keys())}")
    
    assert endpoint_path in paths
    assert "/api/v1/classes/{class_id}" in paths

    # Check POST endpoint
    post_endpoint = paths[endpoint_path]
    assert "post" in post_endpoint
    assert "responses" in post_endpoint["post"]
    assert "201" in post_endpoint["post"]["responses"]
    assert "409" in post_endpoint["post"]["responses"]

    # Check GET list endpoint
    assert "get" in post_endpoint
    assert "responses" in post_endpoint["get"]
    assert "200" in post_endpoint["get"]["responses"]

    # Check GET by ID endpoint
    get_endpoint = paths["/api/v1/classes/{class_id}"]
    assert "get" in get_endpoint
    assert "responses" in get_endpoint["get"]
    assert "200" in get_endpoint["get"]["responses"]
    assert "404" in get_endpoint["get"]["responses"]

    # Check PUT endpoint
    assert "put" in get_endpoint
    assert "responses" in get_endpoint["put"]
    assert "200" in get_endpoint["put"]["responses"]
    assert "404" in get_endpoint["put"]["responses"]

    # Check DELETE endpoint
    assert "delete" in get_endpoint
    assert "responses" in get_endpoint["delete"]
    assert "204" in get_endpoint["delete"]["responses"]
    assert "404" in get_endpoint["delete"]["responses"]

