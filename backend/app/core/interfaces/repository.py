# IRepository interface - Interface Segregation Principle compliant
from abc import ABC, abstractmethod

class IReadRepository(ABC):
    """Read-only repository interface"""

    @abstractmethod
    def get_by_id(self, id):
        """Get entity by ID"""
        pass


class IWriteRepository(ABC):
    """Write-only repository interface"""

    @abstractmethod
    def create(self, entity):
        """Create new entity"""
        pass

    @abstractmethod
    def update(self, entity):
        """Update existing entity"""
        pass

    @abstractmethod
    def delete(self, id):
        """Delete entity by ID"""
        pass


class IRepository(IReadRepository, IWriteRepository):
    """Full repository interface combining read and write operations"""
    pass