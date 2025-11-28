from abc import ABC, abstractmethod

class IUserService(ABC):
    """Interface for user service"""

    @abstractmethod
    def get_user(self, user_id):
        """Get user by ID"""
        pass

    @abstractmethod
    def update_user(self, user_id, user_data):
        """Update user information"""
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """Delete user"""
        pass

    @abstractmethod
    def get_all_users(self):
        """Get all users"""
        pass
