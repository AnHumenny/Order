import re

from pydantic import BaseModel, EmailStr, validator, field_validator
from datetime import datetime

from pydantic_core import PydanticCustomError

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty",
    "111111", "123123", "admin", "letmein",
}

class UserCreate(BaseModel):
    """Schema for creating a new user.

    Used during user registration. Includes email validation.

    Attributes:
        email: User's email address (must be valid email format)
        password: Plain text password (will be hashed)
    """
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 100:
            raise ValueError("Password is too long (max 100 bytes)")
        print("Eто V , ", v)
        print("Eто длина  V , ", len(v))
        if len(v) < 8:
            raise PydanticCustomError(
                "password_too_short",
                "Password must be at least 8 characters long",
            )

        checks = {
            "uppercase": re.search(r"[A-Z]", v),
            "lowercase": re.search(r"[a-z]", v),
            "digit": re.search(r"\d", v),
            "symbol": re.search(r"[^\w\s]", v),
        }

        if sum(bool(x) for x in checks.values()) < 3:
            raise PydanticCustomError(
                "password_too_simple",
                "Password must include at least {required} of: uppercase, lowercase, digit, symbol",
                {"required": 3},
            )

        if v.lower() in COMMON_PASSWORDS:
            raise PydanticCustomError(
                "password_common",
                "Password is too common",
            )

        if re.fullmatch(r"(.)\1{5,}", v):
            raise PydanticCustomError(
                "password_repeated",
                "Password contains repeated characters",
            )

        sequences = ("0123456789", "abcdefghijklmnopqrstuvwxyz")
        v_lower = v.lower()
        for seq in sequences:
            for i in range(len(seq) - 3):
                if seq[i:i + 4] in v_lower:
                    raise PydanticCustomError(
                        "password_sequence",
                        "Password contains sequential characters",
                    )

        return v


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
