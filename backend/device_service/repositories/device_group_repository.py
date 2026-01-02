"""Repository for Device Group data access."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from device_service.models.device_group import DeviceGroup
from shared.schemas.device_group import DeviceGroupCreate, DeviceGroupUpdate


class DeviceGroupRepository:
    """Repository for DeviceGroup database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, group_data: DeviceGroupCreate, school_id: int) -> DeviceGroup:
        """Create a new device group."""
        device_group = DeviceGroup(
            school_id=school_id,
            name=group_data.name,
            description=group_data.description,
        )
        self.db.add(device_group)
        await self.db.commit()
        await self.db.refresh(device_group)
        return device_group

    async def get_by_id(
        self, group_id: int, school_id: Optional[int] = None
    ) -> Optional[DeviceGroup]:
        """
        Get device group by ID.
        
        Args:
            group_id: Device group ID
            school_id: Optional school ID to filter by (for authorization)
        
        Returns:
            DeviceGroup instance or None if not found
        """
        query = select(DeviceGroup).where(
            DeviceGroup.id == group_id,
            DeviceGroup.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(DeviceGroup.school_id == school_id)
        
        query = query.options(selectinload(DeviceGroup.school))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(
        self, name: str, school_id: int
    ) -> Optional[DeviceGroup]:
        """
        Get device group by name within a school.
        
        Args:
            name: Device group name
            school_id: School ID
        
        Returns:
            DeviceGroup instance or None if not found
        """
        result = await self.db.execute(
            select(DeviceGroup).where(
                DeviceGroup.name == name,
                DeviceGroup.school_id == school_id,
                DeviceGroup.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

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
        # Base query
        base_query = select(DeviceGroup).where(
            DeviceGroup.school_id == school_id,
            DeviceGroup.is_deleted == False
        )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = base_query.options(
            selectinload(DeviceGroup.school)
        ).order_by(DeviceGroup.created_at.desc()).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        device_groups = result.scalars().all()
        
        return list(device_groups), total

    async def update(
        self, group_id: int, group_data: DeviceGroupUpdate, school_id: Optional[int] = None
    ) -> Optional[DeviceGroup]:
        """
        Update a device group.
        
        Args:
            group_id: Device group ID
            group_data: Device group update data
            school_id: Optional school ID for authorization
        
        Returns:
            Updated DeviceGroup instance or None if not found
        """
        # Get the device group
        device_group = await self.get_by_id(group_id, school_id)
        if not device_group:
            return None
        
        # Update fields
        if group_data.name is not None:
            device_group.name = group_data.name
        if group_data.description is not None:
            device_group.description = group_data.description
        
        await self.db.commit()
        await self.db.refresh(device_group)
        return device_group

    async def delete(self, group_id: int, school_id: Optional[int] = None) -> bool:
        """
        Soft delete a device group.
        
        Args:
            group_id: Device group ID
            school_id: Optional school ID for authorization
        
        Returns:
            True if deleted, False if not found
        """
        device_group = await self.get_by_id(group_id, school_id)
        if not device_group:
            return False
        
        device_group.is_deleted = True
        await self.db.commit()
        return True

