"""
Driver-related Pydantic schemas for request/response validation.
"""
from typing import Optional
from pydantic import Field, field_validator
import re

from .base_schema import BaseSchema


class DriverBase(BaseSchema):
    """Base driver schema with common fields"""
    license_number: str = Field(..., min_length=1, max_length=100, description="Driver's license number")
    bus_id: int = Field(..., gt=0, description="Assigned bus ID")
    user_id: int = Field(..., gt=0, description="Associated user ID")
    status: str = Field(default='Active', max_length=10, description="Driver status")

    @field_validator('license_number')
    @classmethod
    def validate_license_number(cls, v: str) -> str:
        """Validate and normalize license number"""
        # Remove spaces and convert to uppercase
        license_num = v.replace(" ", "").upper()
        if len(license_num) < 1:
            raise ValueError('License number cannot be empty')
        # Allow alphanumeric and hyphens
        if not re.match(r'^[A-Z0-9\-]+$', license_num):
            raise ValueError('License number can only contain letters, numbers, and hyphens')
        return license_num

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate driver status"""
        valid_statuses = ['Active', 'Inactive', 'Suspended', 'OnLeave']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class DriverCreate(DriverBase):
    """Schema for creating a new driver"""
    pass


class DriverUpdate(BaseSchema):
    """Schema for updating driver information"""
    license_number: Optional[str] = Field(None, min_length=1, max_length=100)
    bus_id: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, max_length=10)

    @field_validator('license_number')
    @classmethod
    def validate_license_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize license number"""
        if v is None:
            return v
        license_num = v.replace(" ", "").upper()
        if len(license_num) < 1:
            raise ValueError('License number cannot be empty')
        if not re.match(r'^[A-Z0-9\-]+$', license_num):
            raise ValueError('License number can only contain letters, numbers, and hyphens')
        return license_num

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate driver status"""
        if v is None:
            return v
        valid_statuses = ['Active', 'Inactive', 'Suspended', 'OnLeave']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class DriverResponse(BaseSchema):
    """Schema for driver response"""
    id: int
    license_number: str
    bus_id: int
    user_id: int
    status: str


class DriverDetailResponse(DriverResponse):
    """Schema for detailed driver response with user and bus info"""
    user_name: Optional[str] = Field(None, description="Driver's name")
    user_phone: Optional[str] = Field(None, description="Driver's phone")
    user_email: Optional[str] = Field(None, description="Driver's email")
    bus_plate_number: Optional[str] = Field(None, description="Bus plate number")
    bus_model: Optional[str] = Field(None, description="Bus model")
    route_id: Optional[int] = Field(None, description="Assigned route ID")
    route_name: Optional[str] = Field(None, description="Route name")


class DriverBusAssignment(BaseSchema):
    """Schema for assigning driver to a bus"""
    bus_id: int = Field(..., gt=0, description="Bus ID to assign")


class DriverStatusUpdate(BaseSchema):
    """Schema for updating driver status"""
    status: str = Field(..., description="New driver status")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate driver status"""
        valid_statuses = ['Active', 'Inactive', 'Suspended', 'OnLeave']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class DriverSearchParams(BaseSchema):
    """Schema for driver search parameters"""
    status: Optional[str] = Field(None, description="Filter by status")
    bus_id: Optional[int] = Field(None, gt=0, description="Filter by bus ID")
    license_number: Optional[str] = Field(None, description="Search by license number")
    user_name: Optional[str] = Field(None, description="Search by driver name")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate driver status"""
        if v is None:
            return v
        valid_statuses = ['Active', 'Inactive', 'Suspended', 'OnLeave']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v
