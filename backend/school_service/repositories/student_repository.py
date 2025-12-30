"""Repository for Student data access."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from school_service.models.student import Student
from shared.schemas.student import StudentCreate, StudentUpdate


class StudentRepository:
    """Repository for Student database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, student_data: StudentCreate) -> Student:
        """Create a new student."""
        student = Student(
            school_id=student_data.school_id,
            admission_number=student_data.admission_number,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            date_of_birth=student_data.date_of_birth,
            gender=student_data.gender,
            class_id=student_data.class_id,
            stream_id=student_data.stream_id,
            parent_phone=student_data.parent_phone,
            parent_email=student_data.parent_email,
        )
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def get_by_id(
        self, student_id: int, school_id: Optional[int] = None
    ) -> Optional[Student]:
        """
        Get student by ID.
        
        Args:
            student_id: Student ID
            school_id: Optional school ID to filter by (for authorization)
        
        Returns:
            Student instance or None if not found
        """
        query = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(Student.school_id == school_id)
        
        query = query.options(
            selectinload(Student.school),
            selectinload(Student.class_),
            selectinload(Student.stream)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_admission_number(
        self, admission_number: str, school_id: int
    ) -> Optional[Student]:
        """
        Get student by admission number within a school.
        
        Args:
            admission_number: Admission number
            school_id: School ID
        
        Returns:
            Student instance or None if not found
        """
        result = await self.db.execute(
            select(Student).where(
                Student.admission_number == admission_number,
                Student.school_id == school_id,
                Student.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

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
            search: Optional search term (searches first_name, last_name, admission_number)
        
        Returns:
            Tuple of (list of students, total count)
        """
        # Base query
        base_query = select(Student).where(
            Student.school_id == school_id,
            Student.is_deleted == False
        )
        
        # Apply filters
        if class_id is not None:
            base_query = base_query.where(Student.class_id == class_id)
        
        if stream_id is not None:
            base_query = base_query.where(Student.stream_id == stream_id)
        
        if search:
            search_term = f"%{search.lower()}%"
            base_query = base_query.where(
                or_(
                    func.lower(Student.first_name).like(search_term),
                    func.lower(Student.last_name).like(search_term),
                    func.lower(Student.admission_number).like(search_term),
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = base_query.options(
            selectinload(Student.school),
            selectinload(Student.class_),
            selectinload(Student.stream)
        ).order_by(Student.created_at.desc()).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        students = result.scalars().all()
        
        return list(students), total

    async def update(
        self, student_id: int, student_data: StudentUpdate, school_id: Optional[int] = None
    ) -> Optional[Student]:
        """
        Update student information.
        
        Args:
            student_id: Student ID
            student_data: Update data
            school_id: Optional school ID to verify ownership
        
        Returns:
            Updated Student instance or None if not found
        """
        # Get existing student
        query = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(Student.school_id == school_id)
        
        result = await self.db.execute(query)
        student = result.scalar_one_or_none()
        
        if not student:
            return None
        
        # Convert Pydantic model to dict, excluding unset fields
        update_dict = student_data.model_dump(exclude_unset=True)
        
        # Update fields
        for key, value in update_dict.items():
            setattr(student, key, value)
        
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def delete(self, student_id: int, school_id: Optional[int] = None) -> bool:
        """
        Soft delete a student.
        
        Args:
            student_id: Student ID
            school_id: Optional school ID to verify ownership
        
        Returns:
            True if deleted, False if not found
        """
        query = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(Student.school_id == school_id)
        
        result = await self.db.execute(query)
        student = result.scalar_one_or_none()
        
        if not student:
            return False
        
        student.is_deleted = True
        await self.db.commit()
        return True

