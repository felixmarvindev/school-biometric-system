"""Service layer for AcademicClass business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from school_service.repositories.class_repository import ClassRepository
from school_service.models.academic_class import AcademicClass
from shared.schemas.class_schema import ClassCreate, ClassUpdate


class ClassService:
    """Service for AcademicClass business logic."""

    def __init__(self, db: AsyncSession):
        self.repository = ClassRepository(db)
        self.db = db

    async def create_class(self, class_data: ClassCreate) -> AcademicClass:
        """
        Create a new class.
        
        Args:
            class_data: Class creation data
            
        Returns:
            Created AcademicClass instance
            
        Raises:
            ValueError: If class name already exists for the school
        """
        # Check for duplicate name within the school
        existing = await self.repository.get_by_name(
            name=class_data.name,
            school_id=class_data.school_id
        )
        if existing:
            raise ValueError(
                f"Class name '{class_data.name}' already exists for this school"
            )
        
        # Create class
        academic_class = await self.repository.create(class_data)
        return academic_class

    async def get_class_by_id(
        self, class_id: int, school_id: Optional[int] = None
    ) -> Optional[AcademicClass]:
        """
        Get class by ID.
        
        Args:
            class_id: Class ID
            school_id: Optional school ID for authorization
        
        Returns:
            AcademicClass instance or None if not found
        """
        return await self.repository.get_by_id(class_id, school_id)

    async def list_classes(self, school_id: int) -> List[AcademicClass]:
        """
        List all classes for a school.
        
        Args:
            school_id: School ID
        
        Returns:
            List of AcademicClass instances
        """
        return await self.repository.list_classes(school_id)

    async def update_class(
        self, class_id: int, class_data: ClassUpdate, school_id: Optional[int] = None
    ) -> Optional[AcademicClass]:
        """
        Update class information.
        
        Args:
            class_id: Class ID
            class_data: Update data
            school_id: Optional school ID for authorization
        
        Returns:
            Updated AcademicClass instance or None if not found
            
        Raises:
            ValueError: If new name already exists for the school
        """
        # If name is being updated, check for duplicates
        if class_data.name is not None and school_id:
            existing = await self.repository.get_by_name(
                name=class_data.name,
                school_id=school_id
            )
            if existing and existing.id != class_id:
                raise ValueError(
                    f"Class name '{class_data.name}' already exists for this school"
                )
        
        return await self.repository.update(class_id, class_data, school_id)

    async def delete_class(
        self, class_id: int, school_id: Optional[int] = None
    ) -> bool:
        """
        Soft delete a class.
        
        Args:
            class_id: Class ID
            school_id: Optional school ID for authorization
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(class_id, school_id)

