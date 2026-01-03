from pydantic import BaseModel, EmailStr
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
