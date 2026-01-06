from pydantic import BaseModel, EmailStr, validator, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for creating a new user.

    Used during user registration. Includes email validation.

    Attributes:
        email: User's email address (must be valid email format)
        password: Plain text password (will be hashed)
    """
    email: EmailStr
    password: str
    #
    # @field_validator('password')
    # def validate_password_length(self, v):
    #     """Validate password length in bytes."""
    #     byte_length = len(v.encode('utf-8'))
    #     if byte_length > 100:
    #         raise ValueError(
    #             f'Password is too long ({byte_length} bytes). '
    #             f'Maximum recommended length is 100 bytes.'
    #         )
    #     return v


class UserRead(BaseModel):
    """Schema for reading user information.

    Used in API responses. Excludes sensitive data like password.

    Attributes:
        id: User identifier
        email: User's email address
        is_active: Account active status
        is_superuser: Admin privileges flag
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM compatibility."""
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response.

    Standard OAuth2 token response format.

    Attributes:
        access_token: JWT access token string
        token_type: Token type (always "bearer" for this implementation)
    """
    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    email: EmailStr
    password: str
