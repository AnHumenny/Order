from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.users.models import User
from app.core.security import hash_password, verify_password, create_access_token


class UserService:
    @staticmethod
    async def register_user(session: AsyncSession, email: str, password: str) -> User:
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=email,
            username=email,
            hashed_password=hash_password(password)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> str:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, str(user.hashed_password)):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return create_access_token({"sub": str(user.id)})
