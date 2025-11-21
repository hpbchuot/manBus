from abc import ABC, abstractmethod

class IBlacklistService(ABC):
    """Interface for token blacklist service"""

    @abstractmethod
    def is_blacklisted(self, token):
        """Check if token is blacklisted"""
        pass

    @abstractmethod
    def add_to_blacklist(self, token):
        """Add token to blacklist"""
        pass

    @abstractmethod
    def remove_from_blacklist(self, token):
        """Remove token from blacklist"""
        pass
