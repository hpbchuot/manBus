"""
User-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field, EmailStr, field_validator, model_validator
import re

from .base_schema import BaseSchema, IDSchema, SoftDeleteSchema, TimestampSchema


class UserBase(BaseSchema):
    """Base user schema with common fields"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    phone: str = Field(..., min_length=10, max_length=11, description="Phone number")
    email: EmailStr = Field(..., description="Email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        # Remove any spaces or dashes
        phone = re.sub(r'[\s\-]', '', v)
        # Check if it's numeric and has correct length
        if not phone.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(phone) not in [10, 11]:
            raise ValueError('Phone number must be 10 or 11 digits')
        return phone

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format"""
        if v is None:
            return v
        # Username can only contain alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    username: str = Field(..., min_length=3, max_length=50, description="Username (required)")
    admin: bool = Field(default=False, description="Admin status")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserRegister(BaseSchema):
    """Schema for user registration (public endpoint)"""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=11)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validate that password and confirm_password match"""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=11)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v is None:
            return v
        phone = re.sub(r'[\s\-]', '', v)
        if not phone.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(phone) not in [10, 11]:
            raise ValueError('Phone number must be 10 or 11 digits')
        return phone


class UserPasswordUpdate(BaseSchema):
    """Schema for updating user password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., min_length=8, max_length=100, description="Confirm new password")

    @model_validator(mode='after')
    def validate_passwords(self):
        """Validate password requirements"""
        if self.new_password != self.confirm_password:
            raise ValueError('New passwords do not match')
        if self.current_password == self.new_password:
            raise ValueError('New password must be different from current password')
        return self

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseSchema):
    """Schema for user response (without sensitive data)"""
    id: int
    name: str
    phone: str
    email: str
    username: Optional[str] = None
    public_id: Optional[str] = None
    role: str
    updated_at: Optional[datetime] = None


class UserDetailResponse(UserResponse):
    """Schema for detailed user response with additional information"""
    deleted_at: Optional[datetime] = None


class UserLogin(BaseSchema):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserLoginResponse(BaseSchema):
    """Schema for login response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse


class UserRoleAssignment(BaseSchema):
    """Schema for assigning role to user"""
    user_id: int = Field(..., gt=0, description="User ID")
    role_id: int = Field(..., gt=0, description="Role ID")


class UserWithRoles(UserResponse):
    """Schema for user response with roles"""
    roles: List[str] = Field(default_factory=list, description="List of role names")


class UserSearchParams(BaseSchema):
    """Schema for user search parameters"""
    query: str = Field(None, description="Search query (name, email, username)")
