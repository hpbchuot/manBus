# Service interfaces for Dependency Inversion Principle

from .auth_service_interface import (
    IAuthService,
    IRegistrationService,
    IAuthenticationService,
    ITokenVerificationService
)
from .user_service_interface import IUserService
from .bus_service_interface import IBusService
from .driver_service_interface import IDriverService
from .route_service_interface import IRouteService, IStopService
from .blacklist_service_interface import IBlacklistService

__all__ = [
    # Auth interfaces (ISP compliant)
    'IAuthService',
    'IRegistrationService',
    'IAuthenticationService',
    'ITokenVerificationService',
    # Domain service interfaces
    'IUserService',
    'IBusService',
    'IDriverService',
    'IRouteService',
    'IStopService',
    'IFeedbackService',
    'IBlacklistService',
    'IRoleService',
]
