"""Service layer for School business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from school_service.repositories.school_repository import SchoolRepository
from school_service.models.school import School
from shared.schemas.school import SchoolCreate, SchoolUpdate


class SchoolService:
    """Service for School business logic."""

    def __init__(self, db: AsyncSession):
        self.repository = SchoolRepository(db)

    async def create_school(self, school_data: SchoolCreate) -> School:
        """
        Create a new school.
        
        Args:
            school_data: School creation data
            
        Returns:
            Created School instance
            
        Raises:
            ValueError: If school code already exists
        """
        # Check for duplicate code
        existing = await self.repository.get_by_code(school_data.code)
        if existing:
            raise ValueError(f"School code '{school_data.code.upper()}' already exists")

        # Create school
        school = await self.repository.create(school_data)
        return school

    async def get_school_by_id(self, school_id: int) -> Optional[School]:
        """Get school by ID."""
        return await self.repository.get_by_id(school_id)

    async def get_school_by_code(self, code: str) -> Optional[School]:
        """Get school by code."""
        return await self.repository.get_by_code(code)

    async def update_school(
        self, school_id: int, school_data: SchoolUpdate
    ) -> Optional[School]:
        """
        Update school information.
        
        Args:
            school_id: ID of school to update
            school_data: Update data (code cannot be changed)
            
        Returns:
            Updated School instance or None if not found
        """
        # Convert Pydantic model to dict, excluding None values
        update_dict = school_data.model_dump(exclude_unset=True)
        
        return await self.repository.update(school_id, update_dict)

