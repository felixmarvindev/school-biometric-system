"""Service layer for Student business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple

from school_service.repositories.student_repository import StudentRepository
from school_service.models.student import Student
from shared.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    """Service for Student business logic."""

    def __init__(self, db: AsyncSession):
        self.repository = StudentRepository(db)
        self.db = db

    async def create_student(self, student_data: StudentCreate) -> Student:
        """
        Create a new student.
        
        Args:
            student_data: Student creation data
            
        Returns:
            Created Student instance
            
        Raises:
            ValueError: If admission number already exists for the school
        """
        # Check for duplicate admission number within the school
        existing = await self.repository.get_by_admission_number(
            admission_number=student_data.admission_number,
            school_id=student_data.school_id
        )
        if existing:
            raise ValueError(
                f"Admission number '{student_data.admission_number}' already exists for this school"
            )
        
        # Create student
        student = await self.repository.create(student_data)
        return student

    async def get_student_by_id(
        self, student_id: int, school_id: Optional[int] = None
    ) -> Optional[Student]:
        """
        Get student by ID.
        
        Args:
            student_id: Student ID
            school_id: Optional school ID for authorization
        
        Returns:
            Student instance or None if not found
        """
        return await self.repository.get_by_id(student_id, school_id)

    async def list_students(
        self,
        school_id: int,
        page: int = 1,
        page_size: int = 50,
        class_id: Optional[int] = None,
        stream_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Student], int]:
        """
        List students with pagination and filtering.
        
        Args:
            school_id: School ID (required)
            page: Page number (1-indexed)
            page_size: Items per page
            class_id: Optional filter by class ID
            stream_id: Optional filter by stream ID
            search: Optional search term
        
        Returns:
            Tuple of (list of students, total count)
        """
        return await self.repository.list_students(
            school_id=school_id,
            page=page,
            page_size=page_size,
            class_id=class_id,
            stream_id=stream_id,
            search=search,
        )

    async def update_student(
        self, student_id: int, student_data: StudentUpdate, school_id: Optional[int] = None
    ) -> Optional[Student]:
        """
        Update student information.
        
        Args:
            student_id: Student ID
            student_data: Update data
            school_id: Optional school ID for authorization
        
        Returns:
            Updated Student instance or None if not found
        """
        return await self.repository.update(student_id, student_data, school_id)

    async def delete_student(
        self, student_id: int, school_id: Optional[int] = None
    ) -> bool:
        """
        Soft delete a student.
        
        Args:
            student_id: Student ID
            school_id: Optional school ID for authorization
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(student_id, school_id)

