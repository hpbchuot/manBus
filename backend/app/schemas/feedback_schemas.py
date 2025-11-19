"""
Feedback-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator

from .base_schema import BaseSchema, TimestampSchema


class FeedbackBase(BaseSchema):
    """Base feedback schema with common fields"""
    content: str = Field(..., min_length=1, max_length=2000, description="Feedback content")
    bus_id: int = Field(..., gt=0, description="Bus ID related to feedback")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate feedback content"""
        content = v.strip()
        if len(content) < 1:
            raise ValueError('Feedback content cannot be empty')
        return content


class FeedbackCreate(FeedbackBase):
    """Schema for creating new feedback (user submission)"""
    # user_id will be extracted from authentication token
    pass


class FeedbackAdminCreate(FeedbackBase):
    """Schema for admin creating feedback on behalf of user"""
    user_id: int = Field(..., gt=0, description="User ID submitting feedback")


class FeedbackUpdate(BaseSchema):
    """Schema for updating feedback"""
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    status: Optional[str] = Field(None, max_length=20)

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate feedback content"""
        if v is None:
            return v
        content = v.strip()
        if len(content) < 1:
            raise ValueError('Feedback content cannot be empty')
        return content

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate feedback status"""
        if v is None:
            return v
        valid_statuses = ['Pending', 'Reviewed', 'Resolved', 'Dismissed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class FeedbackStatusUpdate(BaseSchema):
    """Schema for updating feedback status (admin only)"""
    status: str = Field(..., description="New feedback status")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate feedback status"""
        valid_statuses = ['Pending', 'Reviewed', 'Resolved', 'Dismissed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class FeedbackResponse(BaseSchema):
    """Schema for feedback response"""
    id: int
    status: str
    content: str
    created_at: datetime
    updated_at: datetime
    bus_id: int
    user_id: int


class FeedbackDetailResponse(FeedbackResponse):
    """Schema for detailed feedback response with related information"""
    bus_plate_number: Optional[str] = Field(None, description="Bus plate number")
    bus_name: Optional[str] = Field(None, description="Bus name")
    route_id: Optional[int] = Field(None, description="Route ID")
    route_name: Optional[str] = Field(None, description="Route name")
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")


class FeedbackSearchParams(BaseSchema):
    """Schema for feedback search parameters"""
    status: Optional[str] = Field(None, description="Filter by status")
    bus_id: Optional[int] = Field(None, gt=0, description="Filter by bus ID")
    user_id: Optional[int] = Field(None, gt=0, description="Filter by user ID")
    route_id: Optional[int] = Field(None, gt=0, description="Filter by route ID")
    from_date: Optional[datetime] = Field(None, description="Filter from this date")
    to_date: Optional[datetime] = Field(None, description="Filter to this date")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate feedback status"""
        if v is None:
            return v
        valid_statuses = ['Pending', 'Reviewed', 'Resolved', 'Dismissed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class FeedbackStats(BaseSchema):
    """Schema for feedback statistics"""
    total: int = Field(default=0, description="Total feedback count")
    pending: int = Field(default=0, description="Pending feedback count")
    reviewed: int = Field(default=0, description="Reviewed feedback count")
    resolved: int = Field(default=0, description="Resolved feedback count")
    dismissed: int = Field(default=0, description="Dismissed feedback count")
