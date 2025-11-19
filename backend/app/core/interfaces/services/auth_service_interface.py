from abc import ABC, abstractmethod

class IAuthService(ABC):
    """Interface for authentication service"""

    @abstractmethod
    def register(self, user_data):
        """Register a new user"""
        pass

    @abstractmethod
    def login(self, credentials):
        """Authenticate user and return token"""
        pass

    @abstractmethod
    def logout(self, token):
        """Invalidate token"""
        pass

    @abstractmethod
    def verify_token(self, token):
        """Verify token validity and return user data"""
        pass
