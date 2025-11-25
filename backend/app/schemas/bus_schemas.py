"""
Bus-related Pydantic schemas for request/response validation.
"""
from typing import Optional
from pydantic import Field, field_validator

from .base_schema import BaseSchema, PointSchema


class BusBase(BaseSchema):
    """Base bus schema with common fields"""
    plate_number: str = Field(..., min_length=1, max_length=20, description="Vehicle plate number")
    name: Optional[str] = Field(None, max_length=100, description="Bus name/identifier")
    model: Optional[str] = Field(None, max_length=50, description="Bus model")
    status: str = Field(default='Active', max_length=20, description="Bus status")
    route_id: int = Field(..., gt=0, description="Assigned route ID")

    @field_validator('plate_number')
    @classmethod
    def validate_plate_number(cls, v: str) -> str:
        """Validate and normalize plate number"""
        # Remove spaces and convert to uppercase
        plate = v.replace(" ", "").upper()
        if len(plate) < 1:
            raise ValueError('Plate number cannot be empty')
        return plate

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate bus status"""
        valid_statuses = ['Active', 'Inactive', 'Maintenance', 'Retired']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class BusCreate(BusBase):
    """Schema for creating a new bus"""
    current_location: Optional[PointSchema] = Field(None, description="Initial location (optional)")


class BusUpdate(BaseSchema):
    """Schema for updating bus information"""
    plate_number: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    route_id: Optional[int] = Field(None, gt=0)

    @field_validator('plate_number')
    @classmethod
    def validate_plate_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize plate number"""
        if v is None:
            return v
        plate = v.replace(" ", "").upper()
        if len(plate) < 1:
            raise ValueError('Plate number cannot be empty')
        return plate

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate bus status"""
        if v is None:
            return v
        valid_statuses = ['Active', 'Inactive', 'Maintenance', 'Retired']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class BusLocationUpdate(BaseSchema):
    """Schema for updating bus location (real-time tracking)"""
    location: PointSchema = Field(..., description="New bus location")


class BusResponse(BaseSchema):
    """Schema for bus response"""
    bus_id: int
    plate_number: str
    name: Optional[str] = None
    model: Optional[str] = None
    status: str
    route_id: Optional[int] = None
    current_location: Optional[PointSchema] = None


class BusDetailResponse(BusResponse):
    """Schema for detailed bus response with route information"""
    route_name: Optional[str] = Field(None, description="Name of assigned route")


class BusWithDriver(BusResponse):
    """Schema for bus response with driver information"""
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_license: Optional[str] = None


class BusSearchParams(BaseSchema):
    """Schema for bus search parameters"""
    status: Optional[str] = Field(None, description="Filter by status")
    route_id: Optional[int] = Field(None, gt=0, description="Filter by route ID")
    plate_number: Optional[str] = Field(None, description="Search by plate number")
    nearby_location: Optional[PointSchema] = Field(None, description="Find buses near this location")
    radius_km: Optional[float] = Field(None, gt=0, le=100, description="Search radius in kilometers")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate bus status"""
        if v is None:
            return v
        valid_statuses = ['Active', 'Inactive', 'Maintenance', 'Retired']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class BusStatusUpdate(BaseSchema):
    """Schema for quick status update"""
    status: str = Field(..., description="New bus status")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate bus status"""
        valid_statuses = ['Active', 'Inactive', 'Maintenance', 'Retired']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class BusRouteAssignment(BaseSchema):
    """Schema for assigning bus to a route"""
    route_id: int = Field(..., gt=0, description="Route ID to assign")
