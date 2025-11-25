"""
Pydantic schemas package for ManBus application.
Provides request/response validation schemas for all entities.
"""

# Base schemas
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

# Auth schemas
from .auth_schemas import (
    TokenData,
    TokenResponse,
    RefreshTokenRequest,
    BlacklistTokenRequest,
    BlacklistTokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
)

# User schemas
from .user_schemas import (
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserDetailResponse,
    UserLogin,
    UserLoginResponse,
    UserRoleAssignment,
    UserWithRoles,
    UserSearchParams,
)

# Bus schemas
from .bus_schemas import (
    BusBase,
    BusCreate,
    BusUpdate,
    BusLocationUpdate,
    BusResponse,
    BusDetailResponse,
    BusWithDriver,
    BusSearchParams,
    BusStatusUpdate,
    BusRouteAssignment,
)

# Route and Stop schemas
from .route_schemas import (
    # Stop schemas
    StopBase,
    StopCreate,
    StopUpdate,
    StopResponse,
    StopWithSequence,
    # Route schemas
    RouteBase,
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteDetailResponse,
    RouteWithBuses,
    # Route-Stop management
    RouteStopCreate,
    RouteStopUpdate,
    RouteStopBulkCreate,
    RouteStopReorder,
    # Search params
    RouteSearchParams,
    StopSearchParams,
    NearbyStopsRequest,
)

# Driver schemas
from .driver_schemas import (
    DriverBase,
    DriverCreate,
    DriverUpdate,
    DriverResponse,
    DriverDetailResponse,
    DriverBusAssignment,
    DriverStatusUpdate,
    DriverSearchParams,
)

__all__ = [
    # Base schemas
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

    # Auth schemas
    'TokenData',
    'TokenResponse',
    'RefreshTokenRequest',
    'BlacklistTokenRequest',
    'BlacklistTokenResponse',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    'ChangePasswordRequest',

    # User schemas
    'UserBase',
    'UserCreate',
    'UserRegister',
    'UserUpdate',
    'UserPasswordUpdate',
    'UserResponse',
    'UserDetailResponse',
    'UserLogin',
    'UserLoginResponse',
    'UserRoleAssignment',
    'UserWithRoles',
    'UserSearchParams',

    # Bus schemas
    'BusBase',
    'BusCreate',
    'BusUpdate',
    'BusLocationUpdate',
    'BusResponse',
    'BusDetailResponse',
    'BusWithDriver',
    'BusSearchParams',
    'BusStatusUpdate',
    'BusRouteAssignment',

    # Stop schemas
    'StopBase',
    'StopCreate',
    'StopUpdate',
    'StopResponse',
    'StopWithSequence',

    # Route schemas
    'RouteBase',
    'RouteCreate',
    'RouteUpdate',
    'RouteResponse',
    'RouteDetailResponse',
    'RouteWithBuses',
    'RouteStopCreate',
    'RouteStopUpdate',
    'RouteStopBulkCreate',
    'RouteStopReorder',
    'RouteSearchParams',
    'StopSearchParams',
    'NearbyStopsRequest',

    # Driver schemas
    'DriverBase',
    'DriverCreate',
    'DriverUpdate',
    'DriverResponse',
    'DriverDetailResponse',
    'DriverBusAssignment',
    'DriverStatusUpdate',
    'DriverSearchParams'
]
