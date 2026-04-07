from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.dependencies import oauth2_scheme
from app.core.security import decode_access_token
from app.modules.users.models import User


async def current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Dependency to get the current authenticated user from JWT token.

    Validates the access token and retrieves the corresponding user from database.
    Checks that the user exists and is active.

    Args:
        session: Database session dependency
        token: JWT access token extracted from Authorization header

    Returns:
        User: Authenticated user instance

    Raises:
        HTTPException: 401 if token is invalid or user is inactive
    """

    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await session.scalar(
        select(User).where(User.id == int(user_id))
    )

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user
