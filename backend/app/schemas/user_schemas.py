import datetime
import jwt
# from app.main.model.blacklist import BlacklistToken
from ..config import key

class User:
    def __init__(self, user_data):
        """
        Initialize User from user data dictionary or user ID
        Args:
            user_data: Either a dict with user data or user data from database
        """
        if isinstance(user_data, dict):
            for key, value in user_data.items():
                setattr(self, key, value)
        else:
            # If it's just an ID or other data, store it
            self.id = user_data

    def toJson(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'public_id': self.public_id,
            'username': self.username
        }
    
    
