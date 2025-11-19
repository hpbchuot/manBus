"""
Common schemas used across the application.
Re-exports commonly used base schemas for convenience.
"""
from .base_schema import (
    BaseSchema,
    TimestampSchema,
    SoftDeleteSchema,
    IDSchema,
    PaginationParams,
    PaginatedResponse,
    MessageResponse,
    ErrorDetail,
    ErrorResponse,
    SuccessResponse,
    PointSchema,
    LineStringSchema,
)

__all__ = [
    'BaseSchema',
    'TimestampSchema',
    'SoftDeleteSchema',
    'IDSchema',
    'PaginationParams',
    'PaginatedResponse',
    'MessageResponse',
    'ErrorDetail',
    'ErrorResponse',
    'SuccessResponse',
    'PointSchema',
    'LineStringSchema',
]
