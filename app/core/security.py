import bcrypt
import hashlib
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


MAX_PASSWORD_LEN = 1024

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    Uses SHA-256 first to avoid the 72-byte limit issue.
    """
    if not password:
        raise ValueError("Password cannot be empty")

    sha256_hash = hashlib.sha256(password.encode("utf-8")).digest()

    hashed = bcrypt.hashpw(sha256_hash, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""

    if not plain_password or not hashed_password:
        return False

    sha256_hash = hashlib.sha256(plain_password.encode("utf-8")).digest()
    try:
        return bcrypt.checkpw(sha256_hash, hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """Create a JWT access token with user data.

    Args:
        data: Dictionary containing user claims (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time in minutes

    Returns:
        str: Encoded JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta) # поправить
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)   # поправить
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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
