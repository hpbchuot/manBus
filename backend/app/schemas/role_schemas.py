"""
Role-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field, field_validator

from .base_schema import BaseSchema


class RoleBase(BaseSchema):
    """Base role schema with common fields"""
    role_name: str = Field(..., min_length=1, max_length=100, description="Role name")
    description: Optional[str] = Field(None, description="Role description")

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v: str) -> str:
        """Validate and normalize role name"""
        role_name = v.strip()
        if len(role_name) < 1:
            raise ValueError('Role name cannot be empty')
        # Convert to title case for consistency
        return role_name.title()


class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    pass


class RoleUpdate(BaseSchema):
    """Schema for updating role information"""
    role_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize role name"""
        if v is None:
            return v
        role_name = v.strip()
        if len(role_name) < 1:
            raise ValueError('Role name cannot be empty')
        return role_name.title()


class RoleResponse(BaseSchema):
    """Schema for role response"""
    role_id: int
    role_name: str
    description: Optional[str] = None
    created_at: datetime


class RoleWithUserCount(RoleResponse):
    """Schema for role response with user count"""
    user_count: int = Field(default=0, description="Number of users with this role")


class RoleWithUsers(RoleResponse):
    """Schema for role response with users list"""
    users: List[dict] = Field(default_factory=list, description="Users with this role")


class RoleAssignmentRequest(BaseSchema):
    """Schema for assigning role to user"""
    user_id: int = Field(..., gt=0, description="User ID")
    role_id: int = Field(..., gt=0, description="Role ID")


class RoleBulkAssignmentRequest(BaseSchema):
    """Schema for assigning role to multiple users"""
    user_ids: List[int] = Field(..., min_length=1, description="List of user IDs")
    role_id: int = Field(..., gt=0, description="Role ID")

    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v: List[int]) -> List[int]:
        """Validate user IDs"""
        if not v:
            raise ValueError('At least one user ID is required')
        if any(user_id <= 0 for user_id in v):
            raise ValueError('All user IDs must be positive integers')
        # Remove duplicates
        return list(set(v))


class RoleRemovalRequest(BaseSchema):
    """Schema for removing role from user"""
    user_id: int = Field(..., gt=0, description="User ID")
    role_id: int = Field(..., gt=0, description="Role ID")


class RoleSearchParams(BaseSchema):
    """Schema for role search parameters"""
    role_name: Optional[str] = Field(None, description="Search by role name")
    has_users: Optional[bool] = Field(None, description="Filter roles with/without users")
