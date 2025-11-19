"""Token extraction utility - Single Responsibility Principle"""
from flask import request


class TokenExtractor:
    """Responsible only for extracting tokens from HTTP requests"""

    @staticmethod
    def extract_from_request():
        """
        Extract token from request (Authorization header or query params)

        Returns:
            str: The extracted token
            tuple: (None, error_response, status_code) if extraction fails
        """
        token = None

        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return None, {
                    'message': 'Invalid token format. Use "Bearer <token>"',
                    'status': 'fail'
                }, 401

        # Check for token in request args (query parameters) as fallback
        if not token and 'token' in request.args:
            token = request.args.get('token')

        # No token found
        if not token:
            return None, {
                'message': 'Authentication token is missing',
                'status': 'fail'
            }, 401

        return token, None, None
