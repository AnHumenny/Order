from fastapi import HTTPException
from starlette import status
from app.core.security import verify_password, create_access_token
from app.users.repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo


    async def authenticate_user(self, email: str, password: str) -> str:
        """Authenticate user and return JWT token."""
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, str(user.hashed_password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return create_access_token({"sub": str(user.id)})
