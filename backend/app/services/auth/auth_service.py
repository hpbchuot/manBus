from ..user.user_service import UserService

class AuthService:
    @staticmethod
    def register(db, data):
        # Create user and get the ID
        result = db.query('SELECT fn_create_user(%s, %s, %s, %s, %s)',
                        (data.name, data.phone, data.email, data.username, data.password))
        user_id = result[0]['fn_create_user']
        print(f"Created user with ID: {user_id}")

        # Fetch the full user data using UserService
        user = UserService.get_user(db, user_id)

        if user:
            return user
        else:
            raise Exception("Failed to retrieve created user")
    