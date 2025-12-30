"""Service layer for School business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from school_service.repositories.school_repository import SchoolRepository
from school_service.models.school import School
from shared.schemas.school import SchoolCreate, SchoolUpdate
from shared.schemas.user import UserCreate
from school_service.services.user_service import UserService


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

    async def create_school_with_admin(
        self, school_data: SchoolCreate, admin_data: UserCreate
    ) -> tuple[School, "User"]:  # type: ignore
        """
        Create a new school and its default admin user in a transaction.
        
        If user creation or response preparation fails, the school creation will be rolled back.
        
        Args:
            school_data: School creation data
            admin_data: Admin user creation data (school_id will be set automatically)
            
        Returns:
            Tuple of (Created School instance, Created User instance)
            
        Raises:
            ValueError: If school code already exists or user validation fails
        """
        from school_service.models.user import User
        from shared.schemas.school import SchoolResponse
        from shared.schemas.user import UserResponse
        from shared.schemas.school import SchoolRegistrationResponse
        
        # Check for duplicate code
        existing = await self.repository.get_by_code(school_data.code)
        if existing:
            raise ValueError(f"School code '{school_data.code.upper()}' already exists")

        try:
            # Create school first (without committing)
            school = await self.repository.create_without_commit(school_data)
            
            # Create admin user with the school_id (without committing)
            user_service = UserService(self.repository.db)
            admin_data.school_id = school.id
            admin_user = await user_service.create_user_without_commit(admin_data)
            
            # Validate response can be prepared BEFORE committing
            # This ensures if response preparation would fail, we can still rollback
            try:
                # Validate that objects can be converted to response schemas
                # This catches any data structure issues before committing
                SchoolResponse.model_validate(school)
                UserResponse.model_validate(admin_user)
            except Exception as e:
                # If response validation fails, rollback before raising
                await self.repository.db.rollback()
                raise ValueError(f"Failed to validate response data: {str(e)}") from e
            
            # Only commit if response preparation succeeded
            await self.repository.db.commit()
            
            # Refresh objects to get updated state (timestamps, etc.)
            await self.repository.db.refresh(school)
            await self.repository.db.refresh(admin_user)
            
            return school, admin_user
        except ValueError:
            # Re-raise ValueError as-is (these are expected validation errors)
            raise
        except Exception:
            # Rollback on any other error
            await self.repository.db.rollback()
            raise

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
        # Convert Pydantic model to dict, excluding unset fields but including None values
        # This allows clearing optional fields by setting them to None
        update_dict = school_data.model_dump(exclude_unset=True, exclude_none=False)
        
        return await self.repository.update(school_id, update_dict)

