"""
Route and Stop-related Pydantic schemas for request/response validation.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator

from .base_schema import BaseSchema, LineStringSchema, PointSchema, TimestampSchema


# Stop Schemas
class StopBase(BaseSchema):
    """Base stop schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Stop name")
    location: PointSchema = Field(..., description="Stop location coordinates")


class StopCreate(StopBase):
    """Schema for creating a new bus stop"""
    pass


class StopUpdate(BaseSchema):
    """Schema for updating stop information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[PointSchema] = None


class StopResponse(BaseSchema):
    """Schema for stop response"""
    id: int
    name: str
    location: PointSchema


class StopWithSequence(StopResponse):
    """Schema for stop with sequence number (for route stops)"""
    stop_sequence: int = Field(..., description="Order of stop in route")


# Route Schemas
class RouteBase(BaseSchema):
    """Base route schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Route name")


class RouteCreate(RouteBase):
    """Schema for creating a new route"""
    route_geom: Optional[LineStringSchema] = Field(None, description="Route geometry (path)")
    stop_ids: List[int] = Field(default_factory=list, description="List of stop IDs in order")

    @field_validator('stop_ids')
    @classmethod
    def validate_stop_ids(cls, v: List[int]) -> List[int]:
        """Validate stop IDs list"""
        if len(v) != len(set(v)):
            raise ValueError('Stop IDs must be unique')
        if any(stop_id <= 0 for stop_id in v):
            raise ValueError('All stop IDs must be positive integers')
        return v


class RouteUpdate(BaseSchema):
    """Schema for updating route information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    route_geom: Optional[LineStringSchema] = None
    current_segment: Optional[int] = Field(None, ge=0)


class RouteResponse(BaseSchema):
    """Schema for route response"""
    id: int
    name: str
    route_geom: Optional[LineStringSchema] = None
    current_segment: Optional[int] = None
    updated_at: Optional[datetime] = None


class RouteDetailResponse(RouteResponse):
    """Schema for detailed route response with stops"""
    stops: List[StopWithSequence] = Field(default_factory=list, description="List of stops on route")
    total_stops: int = Field(default=0, description="Total number of stops")


class RouteWithBuses(RouteDetailResponse):
    """Schema for route response with assigned buses"""
    buses: List[dict] = Field(default_factory=list, description="Buses assigned to this route")
    total_buses: int = Field(default=0, description="Total number of buses on route")


# Route-Stop Management
class RouteStopCreate(BaseSchema):
    """Schema for adding a stop to a route"""
    route_id: int = Field(..., gt=0, description="Route ID")
    stop_id: int = Field(..., gt=0, description="Stop ID")
    stop_sequence: int = Field(..., ge=0, description="Position in route sequence")


class RouteStopUpdate(BaseSchema):
    """Schema for updating stop sequence in route"""
    stop_sequence: int = Field(..., ge=0, description="New position in route sequence")


class RouteStopBulkCreate(BaseSchema):
    """Schema for adding multiple stops to a route"""
    route_id: int = Field(..., gt=0, description="Route ID")
    stops: List[dict] = Field(..., min_length=1, description="List of stops with sequences")

    @field_validator('stops')
    @classmethod
    def validate_stops(cls, v: List[dict]) -> List[dict]:
        """Validate stops list"""
        if not v:
            raise ValueError('At least one stop is required')

        sequences = []
        for stop in v:
            if 'stop_id' not in stop or 'stop_sequence' not in stop:
                raise ValueError('Each stop must have stop_id and stop_sequence')
            if stop['stop_id'] <= 0:
                raise ValueError('Stop ID must be positive')
            if stop['stop_sequence'] < 0:
                raise ValueError('Stop sequence must be non-negative')
            sequences.append(stop['stop_sequence'])

        if len(sequences) != len(set(sequences)):
            raise ValueError('Stop sequences must be unique')

        return v


class RouteStopReorder(BaseSchema):
    """Schema for reordering stops on a route"""
    route_id: int = Field(..., gt=0, description="Route ID")
    stop_orders: List[dict] = Field(..., min_length=1, description="New order of stops")

    @field_validator('stop_orders')
    @classmethod
    def validate_stop_orders(cls, v: List[dict]) -> List[dict]:
        """Validate stop orders"""
        if not v:
            raise ValueError('At least one stop is required')

        for item in v:
            if 'stop_id' not in item or 'stop_sequence' not in item:
                raise ValueError('Each item must have stop_id and stop_sequence')

        return v


# Search and Filter Schemas
class RouteSearchParams(BaseSchema):
    """Schema for route search parameters"""
    name: Optional[str] = Field(None, description="Search by route name")
    has_buses: Optional[bool] = Field(None, description="Filter routes with/without buses")


class StopSearchParams(BaseSchema):
    """Schema for stop search parameters"""
    name: Optional[str] = Field(None, description="Search by stop name")
    nearby_location: Optional[PointSchema] = Field(None, description="Find stops near this location")
    radius_km: Optional[float] = Field(None, gt=0, le=50, description="Search radius in kilometers")
    route_id: Optional[int] = Field(None, gt=0, description="Filter by route ID")


class NearbyStopsRequest(BaseSchema):
    """Schema for finding nearby stops"""
    location: PointSchema = Field(..., description="Reference location")
    radius_km: float = Field(default=1.0, gt=0, le=50, description="Search radius in kilometers")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
