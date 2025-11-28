"""
Base schema classes for all Pydantic models in the application.
Provides common patterns and configurations for request/response schemas.
"""
from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal


# Generic type for response data
T = TypeVar('T')


class BaseSchema(BaseModel):
    """
    Base schema with common configuration for all Pydantic models.
    Enables ORM mode for SQLAlchemy compatibility.
    """
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode (formerly orm_mode)
        populate_by_name=True,  # Allow population by field name
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,  # Validate on assignment
        use_enum_values=True,  # Use enum values instead of enum objects
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SoftDeleteSchema(TimestampSchema):
    """Schema with soft delete support"""
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class IDSchema(BaseSchema):
    """Schema with ID field"""
    id: int = Field(..., description="Unique identifier", gt=0)


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response"""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class MessageResponse(BaseSchema):
    """Simple message response schema"""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")


class ErrorDetail(BaseModel):
    """Error detail schema"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseSchema):
    """Error response schema"""
    success: bool = Field(default=False, description="Operation success status")
    message: str = Field(..., description="Error message")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Detailed errors")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response schema"""
    success: bool = Field(default=True, description="Operation success status")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[T] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Coordinate/Location schemas
class PointSchema(BaseSchema):
    """Schema for geographic point (longitude, latitude)"""
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")

    def to_wkt(self) -> str:
        """Convert to Well-Known Text format"""
        return f"POINT({self.longitude} {self.latitude})"

    @classmethod
    def from_wkt(cls, wkt: str) -> "PointSchema":
        """Parse from Well-Known Text format"""
        # Example: "POINT(106.8456 -6.2088)"
        coords = wkt.replace("POINT(", "").replace(")", "").split()
        return cls(longitude=float(coords[0]), latitude=float(coords[1]))


class LineStringSchema(BaseSchema):
    """Schema for geographic linestring (array of points)"""
    coordinates: List[PointSchema] = Field(..., min_length=2, description="Array of coordinates")

    def to_wkt(self) -> str:
        """Convert to Well-Known Text format"""
        coords_str = ", ".join([f"{p.longitude} {p.latitude}" for p in self.coordinates])
        return f"LINESTRING({coords_str})"

    @classmethod
    def from_wkt(cls, wkt: str) -> "LineStringSchema":
        """Parse from Well-Known Text format"""
        # Example: "LINESTRING(106.8456 -6.2088, 106.8556 -6.2188)"
        coords_str = wkt.replace("LINESTRING(", "").replace(")", "")
        points = []
        for coord_pair in coords_str.split(","):
            coords = coord_pair.strip().split()
            points.append(PointSchema(longitude=float(coords[0]), latitude=float(coords[1])))
        return cls(coordinates=points)
