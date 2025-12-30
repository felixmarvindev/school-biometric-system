"""Service layer for Stream business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from school_service.repositories.stream_repository import StreamRepository
from school_service.models.stream import Stream
from shared.schemas.stream_schema import StreamCreate, StreamUpdate
from school_service.services.class_service import ClassService


class StreamService:
    """Service for Stream business logic."""

    def __init__(self, db: AsyncSession):
        self.repository = StreamRepository(db)
        self.class_service = ClassService(db)
        self.db = db

    async def create_stream(self, stream_data: StreamCreate) -> Stream:
        """
        Create a new stream.
        
        Args:
            stream_data: Stream creation data
            
        Returns:
            Created Stream instance
            
        Raises:
            ValueError: If stream name already exists for the class
        """
        # Check for duplicate name within the class
        existing = await self.repository.get_by_name(
            name=stream_data.name,
            class_id=stream_data.class_id
        )
        if existing:
            raise ValueError(
                f"Stream name '{stream_data.name}' already exists for this class"
            )
        
        # Create stream
        stream = await self.repository.create(stream_data)
        return stream

    async def get_stream_by_id(
        self, stream_id: int, school_id: Optional[int] = None
    ) -> Optional[Stream]:
        """
        Get stream by ID.
        
        Args:
            stream_id: Stream ID
            school_id: Optional school ID for authorization
        
        Returns:
            Stream instance or None if not found
        """
        return await self.repository.get_by_id(stream_id, school_id)

    async def list_streams(
        self, school_id: int, class_id: Optional[int] = None
    ) -> List[Stream]:
        """
        List streams for a school, optionally filtered by class.
        
        Args:
            school_id: School ID
            class_id: Optional class ID to filter by
        
        Returns:
            List of Stream instances
        """
        return await self.repository.list_streams(school_id, class_id)

    async def update_stream(
        self, stream_id: int, stream_data: StreamUpdate, school_id: Optional[int] = None
    ) -> Optional[Stream]:
        """
        Update stream information.
        
        Args:
            stream_id: Stream ID
            stream_data: Update data
            school_id: Optional school ID for authorization
        
        Returns:
            Updated Stream instance or None if not found
            
        Raises:
            ValueError: If new name already exists for the class
        """
        # Get existing stream to check class_id
        existing_stream = await self.repository.get_by_id(stream_id, school_id)
        if not existing_stream:
            return None
        
        # If name is being updated, check for duplicates
        if stream_data.name is not None:
            duplicate = await self.repository.get_by_name(
                name=stream_data.name,
                class_id=existing_stream.class_id
            )
            if duplicate and duplicate.id != stream_id:
                raise ValueError(
                    f"Stream name '{stream_data.name}' already exists for this class"
                )
        
        return await self.repository.update(stream_id, stream_data, school_id)

    async def delete_stream(
        self, stream_id: int, school_id: Optional[int] = None
    ) -> bool:
        """
        Soft delete a stream.
        
        Args:
            stream_id: Stream ID
            school_id: Optional school ID for authorization
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(stream_id, school_id)

