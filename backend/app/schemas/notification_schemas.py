"""
Notification-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator, HttpUrl

from .base_schema import BaseSchema


class NotificationBase(BaseSchema):
    """Base notification schema with common fields"""
    message: str = Field(..., min_length=1, max_length=255, description="Notification message")
    type: Optional[str] = Field(None, max_length=50, description="Notification type")
    link: Optional[str] = Field(None, max_length=255, description="Related link/URL")

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate notification message"""
        message = v.strip()
        if len(message) < 1:
            raise ValueError('Notification message cannot be empty')
        return message

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate notification type"""
        if v is None:
            return v
        valid_types = [
            'Info',
            'Warning',
            'Alert',
            'Success',
            'RouteChange',
            'BusDelay',
            'Maintenance',
            'Feedback',
            'System'
        ]
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification"""
    user_id: int = Field(..., gt=0, description="Target user ID")


class NotificationBulkCreate(BaseSchema):
    """Schema for creating notifications for multiple users"""
    message: str = Field(..., min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    link: Optional[str] = Field(None, max_length=255)
    user_ids: list[int] = Field(..., min_length=1, description="List of target user IDs")

    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v: list[int]) -> list[int]:
        """Validate user IDs"""
        if not v:
            raise ValueError('At least one user ID is required')
        if any(user_id <= 0 for user_id in v):
            raise ValueError('All user IDs must be positive integers')
        return v


class NotificationBroadcast(NotificationBase):
    """Schema for broadcasting notification to all users or specific groups"""
    target_group: str = Field(default='all', description="Target group: all, admins, drivers")

    @field_validator('target_group')
    @classmethod
    def validate_target_group(cls, v: str) -> str:
        """Validate target group"""
        valid_groups = ['all', 'admins', 'drivers', 'users']
        if v.lower() not in valid_groups:
            raise ValueError(f'Target group must be one of: {", ".join(valid_groups)}')
        return v.lower()


class NotificationUpdate(BaseSchema):
    """Schema for updating notification"""
    message: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    link: Optional[str] = Field(None, max_length=255)
    read: Optional[bool] = Field(None, description="Mark as read/unread")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate notification type"""
        if v is None:
            return v
        valid_types = [
            'Info',
            'Warning',
            'Alert',
            'Success',
            'RouteChange',
            'BusDelay',
            'Maintenance',
            'Feedback',
            'System'
        ]
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v


class NotificationMarkRead(BaseSchema):
    """Schema for marking notification as read"""
    read: bool = Field(default=True, description="Read status")


class NotificationResponse(BaseSchema):
    """Schema for notification response"""
    id: int
    message: str
    read: bool
    created_at: datetime
    type: Optional[str] = None
    link: Optional[str] = None
    user_id: int


class NotificationDetailResponse(NotificationResponse):
    """Schema for detailed notification response with user info"""
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")


class NotificationSearchParams(BaseSchema):
    """Schema for notification search parameters"""
    user_id: Optional[int] = Field(None, gt=0, description="Filter by user ID")
    read: Optional[bool] = Field(None, description="Filter by read status")
    type: Optional[str] = Field(None, description="Filter by notification type")
    from_date: Optional[datetime] = Field(None, description="Filter from this date")
    to_date: Optional[datetime] = Field(None, description="Filter to this date")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate notification type"""
        if v is None:
            return v
        valid_types = [
            'Info',
            'Warning',
            'Alert',
            'Success',
            'RouteChange',
            'BusDelay',
            'Maintenance',
            'Feedback',
            'System'
        ]
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v


class NotificationStats(BaseSchema):
    """Schema for notification statistics"""
    total: int = Field(default=0, description="Total notifications")
    unread: int = Field(default=0, description="Unread notifications")
    read: int = Field(default=0, description="Read notifications")
    by_type: dict = Field(default_factory=dict, description="Count by notification type")
