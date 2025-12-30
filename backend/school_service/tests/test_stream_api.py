"""Tests for Stream API (Task 024)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from school_service.models.academic_class import AcademicClass
from school_service.models.stream import Stream
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
async def test_stream(test_db: AsyncSession, test_class: AcademicClass) -> Stream:
    """Create a test stream in the database."""
    stream = Stream(
        class_id=test_class.id,
        name="A",
        description="Stream A",
        is_deleted=False,
    )
    test_db.add(stream)
    await test_db.commit()
    await test_db.refresh(stream)
    return stream


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
# Create Stream API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_create_stream_success(
    authenticated_client: AsyncClient, test_class: AcademicClass
):
    """
    Test successful stream creation.
    
    Acceptance Criteria:
    - POST `/api/v1/streams` endpoint exists
    - Returns 201 with created stream data
    """
    stream_data = {
        "class_id": test_class.id,
        "name": "B",
        "description": "Stream B",
    }

    response = await authenticated_client.post("/api/v1/streams", json=stream_data)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert "id" in data
    assert data["name"] == stream_data["name"]
    assert data["description"] == stream_data["description"]
    assert data["class_id"] == test_class.id
    assert data["is_deleted"] is False
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_stream_without_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when no token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    stream_data = {
        "class_id": 1,
        "name": "C",
    }

    response = await client.post("/api/v1/streams", json=stream_data)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_stream_class_not_found(
    authenticated_client: AsyncClient,
):
    """
    Test that creating stream with non-existent class returns 404.
    
    Acceptance Criteria:
    - Returns 404 if class not found
    """
    stream_data = {
        "class_id": 99999,
        "name": "X",
    }

    response = await authenticated_client.post("/api/v1/streams", json=stream_data)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "class" in error_data["detail"].lower() or "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_stream_duplicate_name(
    authenticated_client: AsyncClient, test_class: AcademicClass, test_stream: Stream
):
    """
    Test that duplicate stream name in same class returns 409.
    
    Acceptance Criteria:
    - Returns 409 for duplicate stream name in same class
    """
    stream_data = {
        "class_id": test_class.id,
        "name": test_stream.name,  # Duplicate in same class
        "description": "Duplicate stream",
    }

    response = await authenticated_client.post("/api/v1/streams", json=stream_data)

    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "name" in error_data["detail"].lower() or "already exists" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_stream_same_name_different_class(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
    test_stream: Stream,
):
    """
    Test that same stream name in different class is allowed.
    
    Acceptance Criteria:
    - Same name in different class should succeed
    """
    # Create another class
    class2 = AcademicClass(
        school_id=test_school.id,
        name="Form 2",
        is_deleted=False,
    )
    test_db.add(class2)
    await test_db.commit()
    await test_db.refresh(class2)

    # Create stream with same name in different class
    stream_data = {
        "class_id": class2.id,
        "name": test_stream.name,  # Same name, different class
    }

    response = await authenticated_client.post("/api/v1/streams", json=stream_data)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"


# ============================================================================
# List Streams API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_list_streams_success(
    authenticated_client: AsyncClient, test_stream: Stream
):
    """
    Test successful stream list retrieval.
    
    Acceptance Criteria:
    - GET `/api/v1/streams` endpoint exists
    - Returns list of streams
    """
    response = await authenticated_client.get("/api/v1/streams")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify stream data structure
    stream_item = data[0]
    assert "id" in stream_item
    assert "name" in stream_item
    assert "class_id" in stream_item


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_streams_filter_by_class(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_class: AcademicClass,
    test_school: School,
):
    """
    Test filtering streams by class_id.
    
    Acceptance Criteria:
    - Filtering by class_id works
    """
    # Create another class and stream
    class2 = AcademicClass(
        school_id=test_school.id,
        name="Form 2",
        is_deleted=False,
    )
    test_db.add(class2)
    await test_db.commit()
    await test_db.refresh(class2)

    stream2 = Stream(
        class_id=class2.id,
        name="A",
        is_deleted=False,
    )
    test_db.add(stream2)
    await test_db.commit()

    # List streams filtered by class
    response = await authenticated_client.get(f"/api/v1/streams?class_id={test_class.id}")

    assert response.status_code == 200
    data = response.json()

    # All returned streams should have the same class_id
    for stream in data:
        assert stream["class_id"] == test_class.id


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_streams_only_user_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
    test_user: User,
):
    """
    Test that only streams from user's school classes are returned.
    
    Acceptance Criteria:
    - Returns only streams from authenticated user's school
    """
    # Create another school, class, and stream
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
    await test_db.refresh(class2)

    stream2 = Stream(
        class_id=class2.id,
        name="A",
        is_deleted=False,
    )
    test_db.add(stream2)
    await test_db.commit()

    # List streams - should only get test_school streams
    response = await authenticated_client.get("/api/v1/streams")

    assert response.status_code == 200
    data = response.json()

    # Verify no streams from school2 are returned
    # (We can't directly check school_id, but we can verify streams belong to test_school classes)
    class_ids = {s["class_id"] for s in data}
    assert class2.id not in class_ids


# ============================================================================
# Get Stream by ID API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_get_stream_by_id_success(
    authenticated_client: AsyncClient, test_stream: Stream
):
    """
    Test successful stream retrieval by ID.
    
    Acceptance Criteria:
    - GET `/api/v1/streams/{id}` endpoint exists
    - Returns 200 with stream data
    """
    response = await authenticated_client.get(f"/api/v1/streams/{test_stream.id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert data["id"] == test_stream.id
    assert data["name"] == test_stream.name
    assert data["class_id"] == test_stream.class_id


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_stream_by_id_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent stream returns 404.
    
    Acceptance Criteria:
    - Returns 404 if stream not found
    """
    response = await authenticated_client.get("/api/v1/streams/99999")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_stream_by_id_different_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_user: User,
):
    """
    Test that stream from different school returns 404.
    
    Acceptance Criteria:
    - Returns 404 if stream belongs to different school
    """
    # Create another school, class, and stream
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

    stream2 = Stream(
        class_id=class2.id,
        name="A",
        is_deleted=False,
    )
    test_db.add(stream2)
    await test_db.commit()
    await test_db.refresh(stream2)

    # Try to get stream from different school
    response = await authenticated_client.get(f"/api/v1/streams/{stream2.id}")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "not found" in error_data["detail"].lower()


# ============================================================================
# Update Stream API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_update_stream_success(
    authenticated_client: AsyncClient, test_stream: Stream
):
    """
    Test successful stream update.
    
    Acceptance Criteria:
    - PUT `/api/v1/streams/{id}` endpoint exists
    - Returns 200 with updated stream data
    """
    update_data = {
        "name": "A Updated",
        "description": "Updated description",
    }

    response = await authenticated_client.put(
        f"/api/v1/streams/{test_stream.id}", json=update_data
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify updated fields
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

    # Verify unchanged fields
    assert data["class_id"] == test_stream.class_id


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_stream_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent stream returns 404.
    
    Acceptance Criteria:
    - Returns 404 if stream not found
    """
    update_data = {"name": "Updated"}

    response = await authenticated_client.put("/api/v1/streams/99999", json=update_data)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_stream_duplicate_name(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_class: AcademicClass,
):
    """
    Test that updating to duplicate name in same class returns 409.
    
    Acceptance Criteria:
    - Returns 409 if new name already exists in same class
    """
    # Create two streams in same class
    stream1 = Stream(
        class_id=test_class.id,
        name="A",
        is_deleted=False,
    )
    stream2 = Stream(
        class_id=test_class.id,
        name="B",
        is_deleted=False,
    )
    test_db.add(stream1)
    test_db.add(stream2)
    await test_db.commit()
    await test_db.refresh(stream1)
    await test_db.refresh(stream2)

    # Try to update stream2 to stream1's name
    update_data = {"name": "A"}

    response = await authenticated_client.put(f"/api/v1/streams/{stream2.id}", json=update_data)

    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "name" in error_data["detail"].lower() or "already exists" in error_data["detail"].lower()


# ============================================================================
# Delete Stream API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_stream_success(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_class: AcademicClass,
):
    """
    Test successful stream soft delete.
    
    Acceptance Criteria:
    - DELETE `/api/v1/streams/{id}` endpoint exists
    - Performs soft delete (sets is_deleted = true)
    - Returns 204 No Content on success
    """
    # Create a stream to delete
    stream = Stream(
        class_id=test_class.id,
        name="To Delete",
        is_deleted=False,
    )
    test_db.add(stream)
    await test_db.commit()
    await test_db.refresh(stream)

    response = await authenticated_client.delete(f"/api/v1/streams/{stream.id}")

    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    # Verify stream is soft-deleted (still exists but marked as deleted)
    await test_db.refresh(stream)
    assert stream.is_deleted is True, "Stream should be soft-deleted"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_stream_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent stream returns 404.
    
    Acceptance Criteria:
    - Returns 404 if stream not found
    """
    response = await authenticated_client.delete("/api/v1/streams/99999")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_stream_data_preserved(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_class: AcademicClass,
):
    """
    Test that stream data is preserved after soft delete.
    
    Acceptance Criteria:
    - Stream data is preserved (not hard deleted)
    """
    # Create a stream
    stream = Stream(
        class_id=test_class.id,
        name="Preserve",
        description="Preserve data",
        is_deleted=False,
    )
    test_db.add(stream)
    await test_db.commit()
    await test_db.refresh(stream)

    stream_id = stream.id
    stream_name = stream.name

    # Delete stream
    response = await authenticated_client.delete(f"/api/v1/streams/{stream_id}")
    assert response.status_code == 204

    # Verify stream still exists in database (soft delete)
    stream_check = await test_db.get(Stream, stream_id)
    assert stream_check is not None, "Stream should still exist in database"
    assert stream_check.is_deleted is True, "Stream should be marked as deleted"
    assert stream_check.name == stream_name, "Stream data should be preserved"


# ============================================================================
# API Documentation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_stream_api_documented(client: AsyncClient):
    """
    Test that all stream API endpoints are documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoints are documented
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    paths = schema.get("paths", {})

    # Check all endpoints exist
    streams_path = "/api/v1/streams"
    streams_path_with_slash = "/api/v1/streams/"
    
    # Use whichever format FastAPI provides
    if streams_path in paths:
        endpoint_path = streams_path
    elif streams_path_with_slash in paths:
        endpoint_path = streams_path_with_slash
    else:
        pytest.fail(f"Expected '/api/v1/streams' or '/api/v1/streams/' in paths, got: {list(paths.keys())}")
    
    assert endpoint_path in paths
    assert "/api/v1/streams/{stream_id}" in paths

    # Check POST endpoint
    post_endpoint = paths[endpoint_path]
    assert "post" in post_endpoint
    assert "responses" in post_endpoint["post"]
    assert "201" in post_endpoint["post"]["responses"]
    assert "404" in post_endpoint["post"]["responses"]
    assert "409" in post_endpoint["post"]["responses"]

    # Check GET list endpoint
    assert "get" in post_endpoint
    assert "responses" in post_endpoint["get"]
    assert "200" in post_endpoint["get"]["responses"]

    # Check GET by ID endpoint
    get_endpoint = paths["/api/v1/streams/{stream_id}"]
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

