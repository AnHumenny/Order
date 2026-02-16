from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user, get_current_admin
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserRead, Token
from fastapi.security import OAuth2PasswordRequestForm
from app.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=UserRead)
async def register_user(
        data: UserCreate,
        session: AsyncSession = Depends(get_session)
    ):
    """Register a new user.

    Args:
        data: User registration data (email, username, password)
        session: Database session

    Returns:
        UserRead: Created user data
    """

    repo = UserRepository(session)
    service = UserService(repo)

    user = await service.register_user(
        email=str(data.email),
        username=str(data.username),
        password=data.password
    )

    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT access token.

    Args:
        form_data: OAuth2 form data with username (email) and password
        session: Database session

    Returns:
        Token: JWT access token
    """
    repo = UserRepository(session)
    service = UserService(repo)

    token = await service.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )

    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current authenticated user's information.

    Returns the profile of the user identified by the JWT token.
    """
    return user


@router.delete(
    "/{user_id}",
    summary="Delete user",
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    """Delete user by id."""

    service = UserService(UserRepository(session))
    await service.delete_user(user_id)
    await session.commit()
    return {"status": "deleted"}


@router.get("/", response_model=list[UserRead])
async def list_users(
        session: AsyncSession = Depends(get_session),
        skip: int = 0,
        limit: int = 20,
        admin=Depends(get_current_admin),
):
    """List all users.

    Returns all users from the database. Admin authentication required.

    Args:
        session: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        admin: Current admin user (from dependency)

    Returns:
        list[UserRead]: List of all users
    """

    service = UserService(UserRepository(session))
    users = await service.list_users(skip, limit)

    return [UserRead.model_validate(user) for user in users]
