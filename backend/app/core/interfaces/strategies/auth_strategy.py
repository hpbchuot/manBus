from abc import ABC, abstractmethod

class IAuthenticator(ABC):
    """Interface for credential authentication"""

    @abstractmethod
    def authenticate(self, credentials):
        """Authenticate user credentials and generate token"""
        pass


class ITokenValidator(ABC):
    """Interface for token validation"""

    @abstractmethod
    def validate_token(self, token):
        """Validate and decode token"""
        pass


class IAuthenticationStrategy(IAuthenticator, ITokenValidator):
    """Full authentication strategy combining authentication and validation"""
    pass