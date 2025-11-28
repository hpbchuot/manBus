"""
Cookie Management Middleware
Handles HTTP cookie operations for authentication tokens.

Follows SOLID principles:
- SRP: Single responsibility - cookie operations only
- ISP: Focused interface for cookie management
"""
from flask import Response
from typing import Optional


class CookieManager:
    """
    Middleware for managing HTTP cookies.
    Single Responsibility: Cookie operations
    """

    # Cookie configuration constants
    AUTH_COOKIE_NAME = 'access_token'
    REFRESH_COOKIE_NAME = 'refresh_token'
    DEFAULT_MAX_AGE = 3600  # 1 hour
    REFRESH_MAX_AGE = 86400  # 24 hours

    @staticmethod
    def set_auth_cookie(
        response: Response,
        token: str,
        max_age: int = DEFAULT_MAX_AGE,
        secure: bool = False
    ) -> Response:
        """
        Set authentication cookie on response.

        Args:
            response: Flask response object
            token: JWT access token
            max_age: Cookie expiration in seconds (default: 1 hour)
            secure: Enable secure flag (HTTPS only, default: False for dev)

        Returns:
            Response with authentication cookie set
        """
        response.set_cookie(
            CookieManager.AUTH_COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,      # Cannot be accessed by JavaScript (XSS protection)
            secure=secure,      # Set to True in production with HTTPS
            samesite='Lax'      # CSRF protection
        )
        return response

    @staticmethod
    def clear_auth_cookie(response: Response) -> Response:
        """
        Clear authentication cookie from response.

        Args:
            response: Flask response object

        Returns:
            Response with authentication cookie cleared
        """
        response.set_cookie(
            CookieManager.AUTH_COOKIE_NAME,
            value='',
            max_age=0,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        return response

    @staticmethod
    def set_refresh_cookie(
        response: Response,
        token: str,
        max_age: int = REFRESH_MAX_AGE,
        secure: bool = False
    ) -> Response:
        """
        Set refresh token cookie on response.

        Args:
            response: Flask response object
            token: JWT refresh token
            max_age: Cookie expiration in seconds (default: 24 hours)
            secure: Enable secure flag (HTTPS only, default: False for dev)

        Returns:
            Response with refresh token cookie set
        """
        response.set_cookie(
            CookieManager.REFRESH_COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,      # Cannot be accessed by JavaScript (XSS protection)
            secure=secure,      # Set to True in production with HTTPS
            samesite='Strict'   # Stricter CSRF protection for refresh tokens
        )
        return response

    @staticmethod
    def clear_refresh_cookie(response: Response) -> Response:
        """
        Clear refresh token cookie from response.

        Args:
            response: Flask response object

        Returns:
            Response with refresh token cookie cleared
        """
        response.set_cookie(
            CookieManager.REFRESH_COOKIE_NAME,
            value='',
            max_age=0,
            httponly=True,
            secure=False,
            samesite='Strict'
        )
        return response

    @staticmethod
    def clear_all_auth_cookies(response: Response) -> Response:
        """
        Clear all authentication-related cookies.

        Args:
            response: Flask response object

        Returns:
            Response with all auth cookies cleared
        """
        CookieManager.clear_auth_cookie(response)
        CookieManager.clear_refresh_cookie(response)
        return response
