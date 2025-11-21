"""
CORS Middleware - Refactored to follow Single Responsibility Principle

Responsibilities are now separated:
- CORSConfigLoader: Load configuration from environment
- CORSConfig: Hold configuration data (data structure only)
- CORS functions: Apply CORS headers and handle requests
"""
from flask import request, make_response
from .cors_config_loader import CORSConfigLoader
import logging

logger = logging.getLogger(__name__)


class CORSConfig:
    """CORS configuration data structure - holds configuration only"""

    def __init__(self, config_dict):
        """Initialize with configuration dictionary"""
        self.ENV = config_dict['ENV']
        self.ALLOWED_ORIGINS = config_dict['ALLOWED_ORIGINS']
        self.ALLOW_ALL = config_dict['ALLOW_ALL']
        self.ALLOWED_METHODS = config_dict['ALLOWED_METHODS']
        self.ALLOWED_HEADERS = config_dict['ALLOWED_HEADERS']
        self.ALLOW_CREDENTIALS = config_dict['ALLOW_CREDENTIALS']
        self.MAX_AGE = config_dict['MAX_AGE']
        self.EXPOSE_HEADERS = config_dict['EXPOSE_HEADERS']


# Initialize CORS configuration using loader
_config_dict = CORSConfigLoader.load()
cors_config = CORSConfig(_config_dict)

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