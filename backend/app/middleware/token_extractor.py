"""Token extraction utility - Single Responsibility Principle"""
from flask import request


class TokenExtractor:
    """Responsible only for extracting tokens from HTTP requests"""

    @staticmethod
    def extract_from_request():
        """
        Extract token from request (Cookie, Authorization header, or query params)

        Priority order:
        1. HTTP-only cookie (most secure)
        2. Authorization header (for API clients)
        3. Query parameters (least secure, for special cases)

        Returns:
            str: The extracted token
            tuple: (None, error_response, status_code) if extraction fails
        """
        token = None

        # 1. Check for token in HTTP-only cookie (highest priority)
        if 'access_token' in request.cookies:
            token = request.cookies.get('access_token')

        # 2. Check for token in Authorization header (for API clients without cookies)
        if not token and 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return None, {
                    'message': 'Invalid token format. Use "Bearer <token>"',
                    'status': 'fail'
                }, 401

        # 3. Check for token in request args (query parameters) as fallback
        if not token and 'token' in request.args:
            token = request.args.get('token')

        # No token found
        if not token:
            return None, {
                'message': 'Authentication token is missing',
                'status': 'fail'
            }, 401

        return token, None, None
