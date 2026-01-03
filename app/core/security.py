from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
import jwt
from app.core.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: Password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if passwords match, False otherwise
        """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """Create a JWT access token with user data.

    Args:
        data: Dictionary containing user claims (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time in minutes

    Returns:
        str: Encoded JWT access token
    """
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Args:
        token: JWT access token string

    Returns:
        dict: Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

