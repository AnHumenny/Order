from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.category.models import Category


class CategoryRepository:
    """Repository class for handling database operations for Category entities.

        Implements the data access layer for Category model following the Repository pattern.
        All database operations for categories are centralized in this class.

        Args:
            session: AsyncSession instance for database operations

        Methods:
            create: Create a new category in the database
            get_all: Retrieve all categories with optional ordering
            get_by_id: Retrieve a specific category by its ID
            delete: Remove a category from the database
        """

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, name: str) -> Category:
        """Create and persist a new category in the database.

        Args:
            name: Name of the new category

        Returns:
            Category: The newly created Category instance with generated ID
        """

        category = Category(name=name)
        self.session.add(category)
        await self.session.flush()
        return category


    async def get_all(self, skip, limit) -> list[Category]:
        """Retrieve all categories from the database.

        Returns:
            list[Category]: List of all categories, ordered alphabetically by name
        """

        result = await self.session.execute(
            select(Category).order_by(Category.name)
            .offset(skip)
            .limit(limit)
            .order_by(Category.id)
        )
        return list(result.scalars())


    async def get_by_id(self, category_id: int) -> Category | None:
        """Retrieve a category by its unique identifier.

        Args:
            category_id: ID of the category to retrieve

        Returns:
            Category | None: The Category object if found, None otherwise
        """

        return await self.session.scalar(
            select(Category).where(Category.id == category_id)
        )


    async def delete(self, category_id: int) -> bool:
        """Delete a category from the database by its ID.

        Args:
            category_id: ID of the category to delete

        Returns:
            bool: True if a category was deleted, False if no category with given ID exists
        """

        result = await self.session.execute(
            delete(Category).where(Category.id == category_id)
        )

        if hasattr(result, 'rowcount'):
            return result.rowcount > 0
        return False

