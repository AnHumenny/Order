from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.users.models import User
from app.users.schemas import UserCreate, UserRead, Token
from fastapi.security import OAuth2PasswordRequestForm

from app.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=UserRead)
async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await UserService.register_user(
        session=session,
        email=str(data.email),
        password=data.password,
    )

    user.username = user.username or str(data.email)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT access token."""
    token = await UserService.authenticate_user(
        session=session,
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
