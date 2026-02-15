from typing import Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User


class UserRepository:
    """Repository class for handling database operations for Category entities."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def delete(self, category_id: int) -> bool:
        """Delete a category from the database by its ID.

        Args:
            category_id: ID of the category to delete

        Returns:
            bool: True if a category was deleted, False if no category with given ID exists
        """

        result = await self.session.execute(
            delete(User).where(User.id == category_id)
        )

        if hasattr(result, 'rowcount'):
            return result.rowcount > 0
        return False


    async def get_all_users(self, skip: int, limit: int) -> list[User]:
        """Retrieve all users from the database.

        Returns:
            list[Category]: List of all users, ordered by id
        """

        stmt = (
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.id)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


    async def create(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
