from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.modules.category.repository import CategoryRepository

class CategoryService:
    """Service layer for category business logic.

    Handles the business operations and rules for categories, separating
    concerns from the repository (data access) and API layer (HTTP handling).
    This layer is responsible for error handling, business validations,
    and transaction management.

    Args:
        repo: CategoryRepository instance for data access operations

    Methods:
        create_category: Creates a new category with duplicate name validation
        list_categories: Retrieves all categories
        delete_category: Deletes a category by ID with existence validation
    """

    def __init__(self, repo: CategoryRepository):
        self.repo = repo


    async def create_category(self, name: str):
        """Create a new category with business validations.

        Creates a new category in the system after performing necessary
        business validations. Specifically checks for duplicate category names
        and handles database integrity constraints.

        Args:
            name: Name of the category to create

        Returns:
            Category: The newly created category object
        """

        try:
            return await self.repo.create(name)
        except IntegrityError:
            await self.repo.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )


    async def list_categories(self, skip, limit):
        """Retrieve all categories from the system.

        Returns a complete list of all categories available in the system.
        The categories are ordered alphabetically by name as defined in
        the repository layer.

        Returns:
            list[Category]: List of all category objects
        """
        return await self.repo.get_all(skip, limit)


    async def delete_category(self, category_id: int):
        """Delete a category by ID with existence validation.

        Attempts to delete a category and verifies that the category
        actually existed. If the category doesn't exist, raises a 404 error.

        Args:
            category_id: ID of the category to delete

        Returns:
            None

        Raises:
            HTTPException: 404 Not Found if the category doesn't exist
        """

        deleted = await self.repo.delete(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
