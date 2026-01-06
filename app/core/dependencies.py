from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_session
from app.core.security import decode_access_token
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)) -> User:
    """FastAPI dependency to get the currently authenticated user.

    Validates the JWT access token and retrieves the corresponding user
    from the database. Used as a dependency in protected route handlers.

    Args:
        token: JWT access token extracted from Authorization header
        session: Database session dependency

    Returns:
        User: Authenticated user instance

    Raises:
        HTTPException: 401 if token is invalid or expired
        HTTPException: 404 if user doesn't exist in database
    """

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """FastAPI dependency to get the current admin user.

    Verifies that the authenticated user has superuser/admin privileges.
    Used as a dependency in admin-only route handlers.

    Args:
        current_user: Already authenticated user from get_current_user dependency

    Returns:
        User: Authenticated admin user

    Raises:
        HTTPException: 403 if user doesn't have admin privileges
    """

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
