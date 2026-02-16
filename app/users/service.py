from fastapi import HTTPException
from starlette import status
from app.users.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.users.repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_user(self, email: str, username: str, password: str) -> User:
        """Register a new user."""

        existing_user = await self.repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hash_password(password)
        }

        user = await self.repo.create(user_data)

        if not user.username:
            user.username = email
            await self.repo.session.commit()
            await self.repo.session.refresh(user)

        return user

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get list of all users."""

        users = await self.repo.get_all_users(skip, limit)
        return users or []


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


    async def delete_user(self, user_id: int):
        """Delete a user by ID with existence validation."""

        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
