"""API routes for Student management."""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from school_service.core.database import get_db
from school_service.services.student_service import StudentService
from shared.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    PaginatedStudentResponse,
)
from shared.schemas.user import UserResponse
from school_service.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="""
    Create a new student in the authenticated user's school.
    
    The admission number must be unique within the school.
    """,
    responses={
        201: {
            "description": "Student created successfully",
            "model": StudentResponse,
        },
        409: {
            "description": "Admission number already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Admission number 'STD2024001' already exists for this school"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def create_student(
    student_data: StudentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new student.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student is automatically associated with user's school
    """
    student_service = StudentService(db)
    
    # Ensure student is created for the authenticated user's school
    # Create a new StudentCreate instance with school_id set from authenticated user
    if not current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a school to create students",
        )
    
    student_data_with_school = StudentCreate(
        **student_data.model_dump(exclude={"school_id"}),
        school_id=current_user.school_id,
    )
    
    try:
        student = await student_service.create_student(student_data_with_school)
        return StudentResponse.model_validate(student)
    except ValueError as e:
        # Handle validation errors (duplicate admission number, etc.)
        error_msg = str(e)
        if "admission number" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get(
    "",
    response_model=PaginatedStudentResponse,
    summary="List students",
    description="""
    Get a paginated list of students from the authenticated user's school.
    
    Supports filtering by class, stream, and searching by name or admission number.
    """,
    responses={
        200: {
            "description": "List of students retrieved successfully",
            "model": PaginatedStudentResponse,
        },
    },
)
async def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    stream_id: Optional[int] = Query(None, description="Filter by stream ID"),
    search: Optional[str] = Query(None, min_length=1, description="Search by name or admission number"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List students with pagination and filtering.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns students from user's school
    """
    student_service = StudentService(db)
    
    result = await student_service.list_students(
        school_id=current_user.school_id,
        page=page,
        page_size=page_size,
        class_id=class_id,
        stream_id=stream_id,
        search=search,
    )
    
    students, total = result
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedStudentResponse(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by ID",
    description="""
    Get a specific student by ID.
    
    The student must belong to the authenticated user's school.
    """,
    responses={
        200: {
            "description": "Student retrieved successfully",
            "model": StudentResponse,
        },
        404: {
            "description": "Student not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Student not found"
                    }
                }
            },
        },
    },
)
async def get_student(
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a student by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student must belong to user's school
    """
    student_service = StudentService(db)
    
    student = await student_service.get_student_by_id(
        student_id=student_id,
        school_id=current_user.school_id,
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    return StudentResponse.model_validate(student)


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student",
    description="""
    Update student information.
    
    Admission number and school ID cannot be changed.
    """,
    responses={
        200: {
            "description": "Student updated successfully",
            "model": StudentResponse,
        },
        404: {
            "description": "Student not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Student not found"
                    }
                }
            },
        },
    },
)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a student.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student must belong to user's school
    - **Immutable Fields**: admission_number, school_id
    """
    student_service = StudentService(db)
    
    # Verify student exists and belongs to user's school
    existing_student = await student_service.get_student_by_id(
        student_id=student_id,
        school_id=current_user.school_id,
    )
    
    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    updated_student = await student_service.update_student(
        student_id=student_id,
        student_data=student_data,
        school_id=current_user.school_id,
    )
    
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    return StudentResponse.model_validate(updated_student)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete student (soft delete)",
    description="""
    Soft delete a student (deactivate).
    
    The student data is preserved but marked as deleted.
    This is a soft delete - the student record remains in the database.
    """,
    responses={
        204: {
            "description": "Student deleted successfully",
        },
        404: {
            "description": "Student not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Student not found"
                    }
                }
            },
        },
    },
)
async def delete_student(
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a student.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student must belong to user's school
    - **Operation**: Soft delete (sets is_deleted = true)
    """
    student_service = StudentService(db)
    
    # Verify student exists and belongs to user's school
    existing_student = await student_service.get_student_by_id(
        student_id=student_id,
        school_id=current_user.school_id,
    )
    
    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    deleted = await student_service.delete_student(
        student_id=student_id,
        school_id=current_user.school_id,
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    return None

