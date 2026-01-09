from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.users.models import User
from app.users.schemas import UserCreate, UserRead, Token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=UserRead)
async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user account.

    Creates a new user with email and password. Validates email uniqueness.

    Args:
        data: UserCreate schema with email and password
        session: Database session

    Returns:
        UserRead: Newly created user (without password)

    Raises:
        HTTPException: 400 if email already registered
    """

    result = await session.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.from_orm(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT access token."""
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    print("user = ", user)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current authenticated user's information.

    Returns the profile of the user identified by the JWT token.
    """
    return user


