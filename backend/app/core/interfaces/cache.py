# ICacheService interface
from abc import ABC, abstractmethod

class ICacheService(ABC):
    """Cache abstraction"""
    
    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def set(self, key, value, ttl=None):
        pass
    
    @abstractmethod
    def delete(self, key):
        pass