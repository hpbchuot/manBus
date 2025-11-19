"""
Authentication-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import Field

from .base_schema import BaseSchema


class TokenData(BaseSchema):
    """Schema for JWT token payload data"""
    user_id: int = Field(..., description="User ID")
    username: Optional[str] = Field(None, description="Username")
    public_id: Optional[str] = Field(None, description="User public ID")
    admin: bool = Field(default=False, description="Admin status")
    exp: Optional[int] = Field(None, description="Token expiration timestamp")


class TokenResponse(BaseSchema):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")


class RefreshTokenRequest(BaseSchema):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class BlacklistTokenRequest(BaseSchema):
    """Schema for blacklisting a token"""
    token: str = Field(..., min_length=10, description="Token to blacklist")


class BlacklistTokenResponse(BaseSchema):
    """Schema for blacklist token response"""
    id: int
    token: str
    blacklisted_on: datetime


class PasswordResetRequest(BaseSchema):
    """Schema for password reset request"""
    email: str = Field(..., description="User email address")


class PasswordResetConfirm(BaseSchema):
    """Schema for confirming password reset"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")


class ChangePasswordRequest(BaseSchema):
    """Schema for changing password"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")
