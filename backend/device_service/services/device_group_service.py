"""Service layer for Device Group business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple

from device_service.repositories.device_group_repository import DeviceGroupRepository
from device_service.models.device_group import DeviceGroup
from device_service.models.device import Device
from shared.schemas.device_group import DeviceGroupCreate, DeviceGroupUpdate


class DeviceGroupService:
    """Service for Device Group business logic."""

    def __init__(self, db: AsyncSession):
        self.repository = DeviceGroupRepository(db)
        self.db = db

    async def create_device_group(
        self, group_data: DeviceGroupCreate, school_id: int
    ) -> DeviceGroup:
        """
        Create a new device group.
        
        Args:
            group_data: Device group creation data
            school_id: School ID for the group
            
        Returns:
            Created DeviceGroup instance
            
        Raises:
            ValueError: If group name already exists for the school
        """
        # Check for duplicate name within the school
        existing = await self.repository.get_by_name(
            name=group_data.name,
            school_id=school_id
        )
        if existing:
            raise ValueError(
                f"Device group with name '{group_data.name}' already exists for this school"
            )
        
        # Create device group
        device_group = await self.repository.create(group_data, school_id)
        return device_group

    async def get_device_group_by_id(
        self, group_id: int, school_id: Optional[int] = None
    ) -> Optional[DeviceGroup]:
        """
        Get device group by ID.
        
        Args:
            group_id: Device group ID
            school_id: Optional school ID for authorization
        
        Returns:
            DeviceGroup instance or None if not found
        """
        return await self.repository.get_by_id(group_id, school_id)

    async def list_device_groups(
        self,
        school_id: int,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[DeviceGroup], int]:
        """
        List device groups with pagination.
        
        Args:
            school_id: School ID (required)
            page: Page number (1-indexed)
            page_size: Items per page
        
        Returns:
            Tuple of (list of device groups, total count)
        """
        return await self.repository.list_device_groups(
            school_id=school_id,
            page=page,
            page_size=page_size,
        )

    async def update_device_group(
        self,
        group_id: int,
        group_data: DeviceGroupUpdate,
        school_id: Optional[int] = None
    ) -> Optional[DeviceGroup]:
        """
        Update a device group.
        
        Args:
            group_id: Device group ID
            group_data: Device group update data
            school_id: Optional school ID for authorization
            
        Returns:
            Updated DeviceGroup instance or None if not found
            
        Raises:
            ValueError: If new name conflicts with existing group
        """
        # Get existing device group
        existing_group = await self.repository.get_by_id(group_id, school_id)
        if not existing_group:
            return None
        
        # Check for name conflicts if name is being updated
        update_dict = group_data.model_dump(exclude_unset=True)
        if "name" in update_dict:
            new_name = update_dict["name"]
            # Check if another group (not this one) has this name
            conflict_group = await self.repository.get_by_name(
                name=new_name,
                school_id=existing_group.school_id
            )
            if conflict_group and conflict_group.id != group_id:
                raise ValueError(
                    f"Device group with name '{new_name}' already exists for this school"
                )
        
        # Update device group
        return await self.repository.update(group_id, group_data, school_id)

    async def delete_device_group(
        self, group_id: int, school_id: Optional[int] = None
    ) -> bool:
        """
        Soft delete a device group.
        
        Args:
            group_id: Device group ID
            school_id: Optional school ID for authorization
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(group_id, school_id)

    async def get_device_count(self, group_id: int) -> int:
        """
        Get the number of devices in a device group.
        
        Args:
            group_id: Device group ID
        
        Returns:
            Number of devices in the group (excluding soft-deleted devices)
        """
        result = await self.db.execute(
            select(func.count(Device.id)).where(
                Device.device_group_id == group_id,
                Device.is_deleted == False
            )
        )
        return result.scalar_one() or 0

