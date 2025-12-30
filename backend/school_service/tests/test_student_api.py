"""Tests for Student API (Tasks 015-019)."""

import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.school import School
from school_service.models.user import User
from school_service.models.student import Student, Gender
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
        is_deleted=False,
    )
    test_db.add(stream)
    await test_db.commit()
    await test_db.refresh(stream)
    return stream


@pytest.fixture
async def test_student(
    test_db: AsyncSession, test_school: School, test_class: AcademicClass, test_stream: Stream
) -> Student:
    """Create a test student in the database."""
    student = Student(
        school_id=test_school.id,
        admission_number="STD-001",
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(2010, 5, 15),
        gender=Gender.FEMALE,
        class_id=test_class.id,
        stream_id=test_stream.id,
        parent_phone="+254712345679",
        parent_email="parent@example.com",
        is_deleted=False,
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)
    return student


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
# Task 015: Create Student API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_create_student_success(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test successful student creation.
    
    Acceptance Criteria:
    - POST `/api/v1/students` endpoint exists
    - Endpoint requires authentication (JWT token)
    - Returns 201 with created student data
    """
    student_data = {
        "admission_number": "STD-002",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "2010-05-15",
        "gender": "male",
        "parent_phone": "+254712345680",
        "parent_email": "parent2@example.com",
    }

    response = await authenticated_client.post("/api/v1/students", json=student_data)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert "id" in data
    assert data["admission_number"] == student_data["admission_number"]
    assert data["first_name"] == student_data["first_name"]
    assert data["last_name"] == student_data["last_name"]
    assert data["school_id"] == test_school.id  # Should be auto-assigned
    assert data["date_of_birth"] == student_data["date_of_birth"]
    assert data["gender"] == student_data["gender"]
    assert data["parent_phone"] == student_data["parent_phone"]
    assert data["parent_email"] == student_data["parent_email"]
    assert data["is_deleted"] is False
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_student_without_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when no token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    student_data = {
        "admission_number": "STD-003",
        "first_name": "Test",
        "last_name": "Student",
    }

    response = await client.post("/api/v1/students", json=student_data)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_student_duplicate_admission_number(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test that duplicate admission number returns 409.
    
    Acceptance Criteria:
    - Returns 409 for duplicate admission number
    """
    student_data = {
        "admission_number": test_student.admission_number,  # Duplicate
        "first_name": "Another",
        "last_name": "Student",
    }

    response = await authenticated_client.post("/api/v1/students", json=student_data)

    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "admission number" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_student_validation_errors(authenticated_client: AsyncClient):
    """
    Test that validation errors return 422.
    
    Acceptance Criteria:
    - Returns 422 for validation errors
    """
    # Missing required fields
    student_data = {
        "admission_number": "STD-004",
        # Missing first_name and last_name
    }

    response = await authenticated_client.post("/api/v1/students", json=student_data)

    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_student_auto_assigned_to_school(
    authenticated_client: AsyncClient, test_school: School
):
    """
    Test that student is automatically assigned to authenticated user's school.
    
    Acceptance Criteria:
    - Student is associated with authenticated user's school
    """
    student_data = {
        "admission_number": "STD-005",
        "first_name": "Auto",
        "last_name": "Assigned",
    }

    response = await authenticated_client.post("/api/v1/students", json=student_data)

    assert response.status_code == 201
    data = response.json()
    assert data["school_id"] == test_school.id


@pytest.mark.asyncio
@pytest.mark.api
async def test_create_student_with_class_and_stream(
    authenticated_client: AsyncClient,
    test_school: School,
    test_class: AcademicClass,
    test_stream: Stream,
):
    """
    Test creating student with class and stream assignment.
    
    Acceptance Criteria:
    - Class and stream assignment is optional but works when provided
    """
    student_data = {
        "admission_number": "STD-006",
        "first_name": "Class",
        "last_name": "Stream",
        "class_id": test_class.id,
        "stream_id": test_stream.id,
    }

    response = await authenticated_client.post("/api/v1/students", json=student_data)

    assert response.status_code == 201
    data = response.json()
    assert data["class_id"] == test_class.id
    assert data["stream_id"] == test_stream.id


# ============================================================================
# Task 016: List Students API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_success(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test successful student list retrieval.
    
    Acceptance Criteria:
    - GET `/api/v1/students` endpoint exists
    - Returns paginated response with metadata
    """
    response = await authenticated_client.get("/api/v1/students")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify pagination structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    # Verify items
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    assert data["total"] > 0
    assert data["page"] == 1
    assert data["page_size"] == 50  # Default

    # Verify student data structure
    student = data["items"][0]
    assert "id" in student
    assert "admission_number" in student
    assert "first_name" in student
    assert "last_name" in student


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_pagination(authenticated_client: AsyncClient, test_db: AsyncSession, test_school: School):
    """
    Test pagination works correctly.
    
    Acceptance Criteria:
    - Pagination support (page, page_size)
    """
    # Create multiple students
    for i in range(5):
        student = Student(
            school_id=test_school.id,
            admission_number=f"STD-PAG-{i}",
            first_name=f"Student{i}",
            last_name="Pagination",
            is_deleted=False,
        )
        test_db.add(student)
    await test_db.commit()

    # Test first page
    response = await authenticated_client.get("/api/v1/students?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2

    # Test second page
    response = await authenticated_client.get("/api/v1/students?page=2&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_filter_by_class(
    authenticated_client: AsyncClient, test_student: Student, test_class: AcademicClass
):
    """
    Test filtering by class_id.
    
    Acceptance Criteria:
    - Filtering by class_id works
    """
    response = await authenticated_client.get(f"/api/v1/students?class_id={test_class.id}")

    assert response.status_code == 200
    data = response.json()

    # All returned students should have the same class_id
    for student in data["items"]:
        assert student["class_id"] == test_class.id


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_filter_by_stream(
    authenticated_client: AsyncClient, test_student: Student, test_stream: Stream
):
    """
    Test filtering by stream_id.
    
    Acceptance Criteria:
    - Filtering by stream_id works
    """
    response = await authenticated_client.get(f"/api/v1/students?stream_id={test_stream.id}")

    assert response.status_code == 200
    data = response.json()

    # All returned students should have the same stream_id
    for student in data["items"]:
        assert student["stream_id"] == test_stream.id


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_search_by_name(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test searching by name.
    
    Acceptance Criteria:
    - Search by name works (case-insensitive)
    """
    response = await authenticated_client.get("/api/v1/students?search=jane")

    assert response.status_code == 200
    data = response.json()

    # Should find test_student (Jane Smith)
    found = any(s["id"] == test_student.id for s in data["items"])
    assert found, "Should find student by name search"


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_search_by_admission_number(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test searching by admission number.
    
    Acceptance Criteria:
    - Search by admission_number works
    """
    response = await authenticated_client.get("/api/v1/students?search=STD-001")

    assert response.status_code == 200
    data = response.json()

    # Should find test_student
    found = any(s["id"] == test_student.id for s in data["items"])
    assert found, "Should find student by admission number search"


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_only_user_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
    test_user: User,
):
    """
    Test that only students from user's school are returned.
    
    Acceptance Criteria:
    - Returns only students from authenticated user's school
    """
    # Create another school and student
    school2 = School(
        name="Another School",
        code="AS-001",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    student2 = Student(
        school_id=school2.id,
        admission_number="STD-OTHER",
        first_name="Other",
        last_name="School",
        is_deleted=False,
    )
    test_db.add(student2)
    await test_db.commit()

    # List students - should only get test_school students
    response = await authenticated_client.get("/api/v1/students")

    assert response.status_code == 200
    data = response.json()

    # Verify no students from school2 are returned
    for student in data["items"]:
        assert student["school_id"] == test_school.id
        assert student["school_id"] != school2.id


@pytest.mark.asyncio
@pytest.mark.api
async def test_list_students_excludes_deleted(
    authenticated_client: AsyncClient, test_db: AsyncSession, test_school: School
):
    """
    Test that soft-deleted students are not returned.
    
    Acceptance Criteria:
    - Only active (non-deleted) students returned by default
    """
    # Create a deleted student
    deleted_student = Student(
        school_id=test_school.id,
        admission_number="STD-DELETED",
        first_name="Deleted",
        last_name="Student",
        is_deleted=True,
    )
    test_db.add(deleted_student)
    await test_db.commit()

    # List students - should not include deleted
    response = await authenticated_client.get("/api/v1/students")

    assert response.status_code == 200
    data = response.json()

    # Verify deleted student is not in results
    deleted_ids = [s["id"] for s in data["items"]]
    assert deleted_student.id not in deleted_ids


# ============================================================================
# Task 017: Get Student by ID API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_get_student_by_id_success(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test successful student retrieval by ID.
    
    Acceptance Criteria:
    - GET `/api/v1/students/{id}` endpoint exists
    - Returns 200 with student data
    """
    response = await authenticated_client.get(f"/api/v1/students/{test_student.id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert data["id"] == test_student.id
    assert data["admission_number"] == test_student.admission_number
    assert data["first_name"] == test_student.first_name
    assert data["last_name"] == test_student.last_name
    assert data["school_id"] == test_student.school_id


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_student_by_id_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent student returns 404.
    
    Acceptance Criteria:
    - Returns 404 if student not found
    """
    response = await authenticated_client.get("/api/v1/students/99999")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_student_by_id_different_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_user: User,
):
    """
    Test that student from different school returns 404.
    
    Acceptance Criteria:
    - Returns 404 if student belongs to different school
    """
    # Create another school and student
    school2 = School(
        name="Another School",
        code="AS-002",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    student2 = Student(
        school_id=school2.id,
        admission_number="STD-OTHER-2",
        first_name="Other",
        last_name="Student",
        is_deleted=False,
    )
    test_db.add(student2)
    await test_db.commit()
    await test_db.refresh(student2)

    # Try to get student from different school
    response = await authenticated_client.get(f"/api/v1/students/{student2.id}")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    error_data = response.json()
    assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.api
async def test_get_student_by_id_without_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when no token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    response = await client.get("/api/v1/students/1")

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


# ============================================================================
# Task 018: Update Student API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_update_student_success(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test successful student update.
    
    Acceptance Criteria:
    - PUT `/api/v1/students/{id}` endpoint exists
    - Returns 200 with updated student data
    """
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "parent_phone": "+254798765432",
    }

    response = await authenticated_client.put(
        f"/api/v1/students/{test_student.id}", json=update_data
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify updated fields
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["parent_phone"] == update_data["parent_phone"]

    # Verify unchanged fields
    assert data["admission_number"] == test_student.admission_number
    assert data["school_id"] == test_student.school_id


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_student_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent student returns 404.
    
    Acceptance Criteria:
    - Returns 404 if student not found
    """
    update_data = {"first_name": "Updated"}

    response = await authenticated_client.put("/api/v1/students/99999", json=update_data)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_student_different_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_user: User,
):
    """
    Test that updating student from different school returns 404.
    
    Acceptance Criteria:
    - Returns 404 if student belongs to different school
    """
    # Create another school and student
    school2 = School(
        name="Another School",
        code="AS-003",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    student2 = Student(
        school_id=school2.id,
        admission_number="STD-OTHER-3",
        first_name="Other",
        last_name="Student",
        is_deleted=False,
    )
    test_db.add(student2)
    await test_db.commit()
    await test_db.refresh(student2)

    update_data = {"first_name": "Updated"}

    response = await authenticated_client.put(f"/api/v1/students/{student2.id}", json=update_data)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_student_immutable_fields(
    authenticated_client: AsyncClient, test_student: Student
):
    """
    Test that admission_number and school_id cannot be updated.
    
    Acceptance Criteria:
    - Admission number cannot be updated (immutable)
    - School ID cannot be updated (immutable)
    """
    original_admission = test_student.admission_number
    original_school_id = test_student.school_id

    # Try to update immutable fields (should be ignored by schema)
    update_data = {
        "admission_number": "NEW-ADMISSION",  # Should be ignored
        "school_id": 99999,  # Should be ignored
        "first_name": "Updated",
    }

    response = await authenticated_client.put(
        f"/api/v1/students/{test_student.id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()

    # Verify immutable fields unchanged
    assert data["admission_number"] == original_admission
    assert data["school_id"] == original_school_id
    assert data["first_name"] == "Updated"  # Mutable field updated


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_student_class_and_stream(
    authenticated_client: AsyncClient,
    test_student: Student,
    test_class: AcademicClass,
    test_stream: Stream,
):
    """
    Test updating class and stream assignment.
    
    Acceptance Criteria:
    - Class and stream assignment can be updated
    """
    update_data = {
        "class_id": test_class.id,
        "stream_id": test_stream.id,
    }

    response = await authenticated_client.put(
        f"/api/v1/students/{test_student.id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["class_id"] == test_class.id
    assert data["stream_id"] == test_stream.id


# ============================================================================
# Task 019: Delete Student API Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_student_success(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
):
    """
    Test successful student soft delete.
    
    Acceptance Criteria:
    - DELETE `/api/v1/students/{id}` endpoint exists
    - Performs soft delete (sets is_deleted = true)
    - Returns 204 No Content on success
    """
    # Create a student to delete
    student = Student(
        school_id=test_school.id,
        admission_number="STD-TO-DELETE",
        first_name="Delete",
        last_name="Me",
        is_deleted=False,
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)

    response = await authenticated_client.delete(f"/api/v1/students/{student.id}")

    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    # Verify student is soft-deleted (still exists but marked as deleted)
    await test_db.refresh(student)
    assert student.is_deleted is True, "Student should be soft-deleted"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_student_not_found(authenticated_client: AsyncClient):
    """
    Test that non-existent student returns 404.
    
    Acceptance Criteria:
    - Returns 404 if student not found
    """
    response = await authenticated_client.delete("/api/v1/students/99999")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_student_different_school(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_user: User,
):
    """
    Test that deleting student from different school returns 404.
    
    Acceptance Criteria:
    - Returns 404 if student belongs to different school
    """
    # Create another school and student
    school2 = School(
        name="Another School",
        code="AS-004",
        is_deleted=False,
    )
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school2)

    student2 = Student(
        school_id=school2.id,
        admission_number="STD-OTHER-4",
        first_name="Other",
        last_name="Student",
        is_deleted=False,
    )
    test_db.add(student2)
    await test_db.commit()
    await test_db.refresh(student2)

    response = await authenticated_client.delete(f"/api/v1/students/{student2.id}")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_student_data_preserved(
    authenticated_client: AsyncClient,
    test_db: AsyncSession,
    test_school: School,
):
    """
    Test that student data is preserved after soft delete.
    
    Acceptance Criteria:
    - Student data is preserved (not hard deleted)
    """
    # Create a student
    student = Student(
        school_id=test_school.id,
        admission_number="STD-PRESERVE",
        first_name="Preserve",
        last_name="Data",
        is_deleted=False,
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)

    student_id = student.id
    admission_number = student.admission_number

    # Delete student
    response = await authenticated_client.delete(f"/api/v1/students/{student_id}")
    assert response.status_code == 204

    # Verify student still exists in database (soft delete)
    student_check = await test_db.get(Student, student_id)
    assert student_check is not None, "Student should still exist in database"
    assert student_check.is_deleted is True, "Student should be marked as deleted"
    assert student_check.admission_number == admission_number, "Student data should be preserved"


@pytest.mark.asyncio
@pytest.mark.api
async def test_delete_student_without_token(client: AsyncClient):
    """
    Test that endpoint returns 401 when no token is provided.
    
    Acceptance Criteria:
    - Returns 401 if not authenticated
    """
    response = await client.delete("/api/v1/students/1")

    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


# ============================================================================
# API Documentation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.api
async def test_student_api_documented(client: AsyncClient):
    """
    Test that all student API endpoints are documented in OpenAPI.
    
    Acceptance Criteria:
    - API endpoints are documented
    """
    # Get OpenAPI schema
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    paths = schema.get("paths", {})

    # Check all endpoints exist (FastAPI may show with or without trailing slash)
    students_path = "/api/v1/students"
    students_path_with_slash = "/api/v1/students/"
    
    # Use whichever format FastAPI provides
    if students_path in paths:
        post_endpoint_path = students_path
    elif students_path_with_slash in paths:
        post_endpoint_path = students_path_with_slash
    else:
        pytest.fail(f"Expected '/api/v1/students' or '/api/v1/students/' in paths, got: {list(paths.keys())}")
    
    assert post_endpoint_path in paths
    assert "/api/v1/students/{student_id}" in paths

    # Check POST endpoint
    post_endpoint = paths[post_endpoint_path]
    assert "post" in post_endpoint
    assert "responses" in post_endpoint["post"]
    assert "201" in post_endpoint["post"]["responses"]
    assert "409" in post_endpoint["post"]["responses"]
    assert "422" in post_endpoint["post"]["responses"]

    # Check GET list endpoint
    assert "get" in post_endpoint
    assert "responses" in post_endpoint["get"]
    assert "200" in post_endpoint["get"]["responses"]

    # Check GET by ID endpoint
    get_endpoint = paths["/api/v1/students/{student_id}"]
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

