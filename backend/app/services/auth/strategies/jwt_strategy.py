import jwt
from datetime import datetime, timedelta
from app.core.interfaces.strategies.auth_strategy import IAuthenticationStrategy

class JWTAuthenticationStrategy(IAuthenticationStrategy):
    """JWT-based authentication"""

    def __init__(self, secret_key, algorithm='HS256', token_expiry_hours=24):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._token_expiry_hours = token_expiry_hours

    def authenticate(self, credentials):
        """
        Generate JWT token from credentials
        credentials should contain: {'uuid': user_public_id, 'username': username}
        """
        if not credentials or 'uuid' not in credentials:
            raise ValueError("Credentials must contain 'uuid'")

        if credentials['uuid'] is None or credentials['uuid'] == '':
            raise ValueError("UUID cannot be None or empty")

        payload = {
            'uuid': credentials['uuid'],
            'username': credentials.get('username', ''),
            'exp': datetime.utcnow() + timedelta(hours=self._token_expiry_hours),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return {'token': token, 'expires_in': self._token_expiry_hours * 3600}

    def validate_token(self, token):
        """
        Validate and decode JWT token
        Returns decoded payload if valid
        Raises jwt exceptions if invalid
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")