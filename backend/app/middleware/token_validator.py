"""Token validation utility - Single Responsibility Principle"""
import jwt
import logging

logger = logging.getLogger(__name__)


class TokenValidator:
    """Responsible only for validating and decoding JWT tokens"""

    def __init__(self, secret_key, algorithm='HS256'):
        self._secret_key = secret_key
        self._algorithm = algorithm

    def validate(self, token):
        """
        Validate and decode JWT token

        Args:
            token: JWT token string

        Returns:
            dict: Decoded payload if successful
            tuple: (None, error_response, status_code) if validation fails
        """
        try:
            # Decode the token
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload, None, None

        except jwt.ExpiredSignatureError:
            return None, {
                'message': 'Token has expired. Please log in again.',
                'status': 'fail'
            }, 401

        except jwt.InvalidTokenError:
            return None, {
                'message': 'Invalid token. Please log in again.',
                'status': 'fail'
            }, 401

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None, {
                'message': 'Authentication failed',
                'status': 'fail'
            }, 500
