from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import UserRead, Token
from fastapi.security import OAuth2PasswordRequestForm
from app.modules.auth.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


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
