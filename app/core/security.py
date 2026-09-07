import bcrypt
import hashlib
from dotenv import load_dotenv
from fastapi import HTTPException
from jose import ExpiredSignatureError
from jwt import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
from starlette import status
from typing import Any, cast


load_dotenv()

def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise RuntimeError("SECRET_KEY is not configured")

    return secret_key

SECRET_KEY: str = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600


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
        return bcrypt.checkpw(
            sha256_hash,
            hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(
        data: dict[str, Any],
        expires_delta: int | None = None
) -> str:
    """Create a JWT access token with user data."""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT access token."""

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return cast(dict[str, Any], payload)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )