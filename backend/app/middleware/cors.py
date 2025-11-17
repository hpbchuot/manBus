from flask import request, jsonify, make_response
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class CORSConfig:
    """CORS configuration class"""
    def __init__(self):
        # Get environment
        self.ENV = os.getenv('FLASK_ENV', 'development')

        # Get allowed origins from environment or use defaults
        origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
        if origins_env:
            self.ALLOWED_ORIGINS = [origin.strip() for origin in origins_env.split(',')]
        else:
            # Default origins based on environment
            if self.ENV == 'production':
                self.ALLOWED_ORIGINS = []  # Must be explicitly set in production
            else:
                self.ALLOWED_ORIGINS = [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:5173",  # Vite default
                    "http://127.0.0.1:5173",
                ]

        # Allow all origins in development if wildcard is set
        self.ALLOW_ALL = os.getenv('CORS_ALLOW_ALL', 'false').lower() == 'true'

        # Methods
        methods_env = os.getenv('CORS_ALLOWED_METHODS', '')
        if methods_env:
            self.ALLOWED_METHODS = [method.strip() for method in methods_env.split(',')]
        else:
            self.ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

        # Headers
        headers_env = os.getenv('CORS_ALLOWED_HEADERS', '')
        if headers_env:
            self.ALLOWED_HEADERS = [header.strip() for header in headers_env.split(',')]
        else:
            self.ALLOWED_HEADERS = [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Accept",
                "Origin"
            ]

        # Credentials
        self.ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'

        # Max age for preflight cache
        self.MAX_AGE = int(os.getenv('CORS_MAX_AGE', '3600'))

        # Expose headers
        expose_headers_env = os.getenv('CORS_EXPOSE_HEADERS', '')
        if expose_headers_env:
            self.EXPOSE_HEADERS = [header.strip() for header in expose_headers_env.split(',')]
        else:
            self.EXPOSE_HEADERS = ["Content-Range", "X-Content-Range"]

        # Log configuration
        if self.ENV == 'production' and (self.ALLOW_ALL or not self.ALLOWED_ORIGINS):
            logger.warning("⚠️  CORS: Running in production without specific allowed origins!")

        logger.info(f"CORS initialized - ENV: {self.ENV}, Allow all: {self.ALLOW_ALL}")

# Initialize CORS configuration
cors_config = CORSConfig()

def is_origin_allowed(origin):
    """
    Check if the origin is allowed
    Args:
        origin: The origin header from the request
    Returns:
        bool: True if origin is allowed, False otherwise
    """
    if not origin:
        return False

    # Allow all origins if configured (development only)
    if cors_config.ALLOW_ALL:
        return True

    # Check if origin is in allowed list
    if origin in cors_config.ALLOWED_ORIGINS:
        return True

    # Check for wildcard patterns (e.g., *.example.com)
    for allowed_origin in cors_config.ALLOWED_ORIGINS:
        if allowed_origin.startswith('*'):
            domain = allowed_origin[1:]  # Remove the *
            if origin.endswith(domain):
                return True

    return False

def add_cors_headers(response):
    """
    Add CORS headers to response
    Args:
        response: Flask response object
    Returns:
        response: Response with CORS headers added
    """
    origin = request.headers.get('Origin')

    # Set Access-Control-Allow-Origin
    if cors_config.ALLOW_ALL:
        response.headers['Access-Control-Allow-Origin'] = '*'
        # Note: When using wildcard, credentials must be false
        if cors_config.ALLOW_CREDENTIALS:
            logger.warning("CORS: Credentials cannot be used with wildcard origin. Setting to specific origin.")
            if origin and is_origin_allowed(origin):
                response.headers['Access-Control-Allow-Origin'] = origin
    elif origin and is_origin_allowed(origin):
        response.headers['Access-Control-Allow-Origin'] = origin
    elif len(cors_config.ALLOWED_ORIGINS) == 1:
        # If only one origin is configured, use it
        response.headers['Access-Control-Allow-Origin'] = cors_config.ALLOWED_ORIGINS[0]

    # Set other CORS headers
    response.headers['Access-Control-Allow-Methods'] = ', '.join(cors_config.ALLOWED_METHODS)
    response.headers['Access-Control-Allow-Headers'] = ', '.join(cors_config.ALLOWED_HEADERS)

    if cors_config.ALLOW_CREDENTIALS and not cors_config.ALLOW_ALL:
        response.headers['Access-Control-Allow-Credentials'] = 'true'

    response.headers['Access-Control-Max-Age'] = str(cors_config.MAX_AGE)

    if cors_config.EXPOSE_HEADERS:
        response.headers['Access-Control-Expose-Headers'] = ', '.join(cors_config.EXPOSE_HEADERS)

    return response

def handle_preflight():
    """
    Handle OPTIONS preflight requests
    Returns:
        response: Empty response with CORS headers
    """
    response = make_response('', 204)
    return add_cors_headers(response)

def init_cors(app):
    """
    Initialize CORS middleware for Flask app
    Args:
        app: Flask application instance
    """

    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses"""
        return add_cors_headers(response)

    @app.before_request
    def before_request():
        """Handle preflight OPTIONS requests"""
        if request.method == 'OPTIONS':
            return handle_preflight()

    logger.info("CORS middleware initialized")