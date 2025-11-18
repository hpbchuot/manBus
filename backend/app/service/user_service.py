# Database operations should be passed as parameters to avoid circular imports
from ..model.user import User

class UserService:
    """Base service for user-related database operations"""

    @staticmethod
    def get_user(db, user_id):
        """Fetch user by ID"""
        user_data = db.fetch_one(
            '''SELECT id, public_id, username, email, name, phone
               FROM "users" WHERE id = %s''',
            (user_id,)
        )
        if user_data:
            return User(dict(user_data))
        return None