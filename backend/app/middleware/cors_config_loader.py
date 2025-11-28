"""CORS Configuration Loader - Single Responsibility Principle"""
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class CORSConfigLoader:
    """Responsible only for loading CORS configuration from environment"""

    @staticmethod
    def load():
        """
        Load CORS configuration from environment variables

        Returns:
            dict: Configuration dictionary
        """
        env = os.getenv('FLASK_ENV', 'development')

        # Load allowed origins
        origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
        if origins_env:
            allowed_origins = [origin.strip() for origin in origins_env.split(',')]
        else:
            # Default origins based on environment
            if env == 'production':
                allowed_origins = []  # Must be explicitly set in production
            else:
                allowed_origins = [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:5173",  # Vite default
                    "http://127.0.0.1:5173",
                ]

        # Load other settings
        allow_all = os.getenv('CORS_ALLOW_ALL', 'false').lower() == 'true'

        methods_env = os.getenv('CORS_ALLOWED_METHODS', '')
        allowed_methods = [method.strip() for method in methods_env.split(',')] if methods_env else [
            "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
        ]

        headers_env = os.getenv('CORS_ALLOWED_HEADERS', '')
        allowed_headers = [header.strip() for header in headers_env.split(',')] if headers_env else [
            "Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"
        ]

        allow_credentials = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
        max_age = int(os.getenv('CORS_MAX_AGE', '3600'))

        expose_headers_env = os.getenv('CORS_EXPOSE_HEADERS', '')
        expose_headers = [header.strip() for header in expose_headers_env.split(',')] if expose_headers_env else [
            "Content-Range", "X-Content-Range", "Authorization"
        ]

        # Validate and warn
        if env == 'production' and (allow_all or not allowed_origins):
            logger.warning("⚠️  CORS: Running in production without specific allowed origins!")

        logger.info(f"CORS configuration loaded - ENV: {env}, Allow all: {allow_all}")

        return {
            'ENV': env,
            'ALLOWED_ORIGINS': allowed_origins,
            'ALLOW_ALL': allow_all,
            'ALLOWED_METHODS': allowed_methods,
            'ALLOWED_HEADERS': allowed_headers,
            'ALLOW_CREDENTIALS': allow_credentials,
            'MAX_AGE': max_age,
            'EXPOSE_HEADERS': expose_headers
        }
