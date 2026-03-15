from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.modules.category.repository import CategoryRepository
from app.modules.category.schemas import CategoryCreate, CategoryUpdate


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
        get_category_by_id: Retrieves a specific category by ID
        get_root_categories: Retrieves all root categories (no parent)
        get_subcategories: Retrieves direct subcategories of a category
        get_category_tree: Retrieves full category tree
        get_category_path: Retrieves path from root to category
        update_category: Updates a category
        delete_category: Deletes a category by ID with existence validation
        get_products_count: Gets count of products in a category
    """

    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def create_category(self, data: CategoryCreate):
        """Create a new category with business validations.

        Creates a new category in the system after performing necessary
        business validations. Specifically checks for duplicate category names
        and validates parent category existence.

        Args:
            data: CategoryCreate schema with name and optional parent_id

        Returns:
            Category: The newly created category object

        Raises:
            HTTPException: 400 if parent category doesn't exist
            HTTPException: 409 if category name already exists
        """
        if data.parent_id:
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parent category with id {data.parent_id} not found",
                )

        try:
            return await self.repo.create_from_schema(data)
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )


    async def list_categories(
            self,
            skip: int = 0,
            limit: int = 100,
            include_hierarchy: bool = False
    ) -> List:
        """Retrieve all categories from the system.

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            include_hierarchy: Whether to include parent/children info

        Returns:
            list[Category]: List of category objects
        """
        return await self.repo.get_all(skip, limit, include_hierarchy)

    async def get_category_by_id(
            self,
            category_id: int,
            include_children: bool = False
    ):
        """Get a specific category by ID.

        Args:
            category_id: ID of the category to retrieve
            include_children: Whether to load subcategories

        Returns:
            Category: Category object if found

        Raises:
            HTTPException: 404 if category not found
        """
        category = await self.repo.get_by_id(category_id, include_children)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )
        return category


    async def get_root_categories(self) -> List:
        """Get all root categories (categories without a parent).

        Returns:
            list[Category]: List of root categories
        """
        return await self.repo.get_root_categories()


    async def get_subcategories(self, category_id: int) -> List:
        """Get direct subcategories of a category.

        Args:
            category_id: ID of the parent category

        Returns:
            list[Category]: List of direct subcategories

        Raises:
            HTTPException: 404 if parent category not found
        """

        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        return await self.repo.get_children(category_id)

    async def get_category_tree(
            self,
            category_id: int,
            max_depth: Optional[int] = None
    ):
        """Get full category tree with all descendants.

        Args:
            category_id: ID of the root category for the tree
            max_depth: Maximum depth of the tree (optional)

        Returns:
            CategoryTree: Category tree structure

        Raises:
            HTTPException: 404 if category not found
        """

        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        return await self.repo.get_category_tree(category_id, max_depth)

    async def get_category_path(self, category_id: int) -> List:
        """Get full path from root to the specified category.

        Args:
            category_id: ID of the category

        Returns:
            list[Category]: List of categories from root to target

        Raises:
            HTTPException: 404 if category not found
        """

        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        return await self.repo.get_category_path(category_id)


    async def update_category(self, category_id: int, data: CategoryUpdate):
        """Update a category.

        Args:
            category_id: ID of the category to update
            data: Update data (name, parent_id)

        Returns:
            Category: Updated category object

        Raises:
            HTTPException: 404 if category not found
            HTTPException: 400 if validation fails
            HTTPException: 409 if name already exists
        """

        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        if data.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent",
            )

        if data.parent_id:
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parent category with id {data.parent_id} not found",
                )

            if await self._would_create_cycle(category_id, data.parent_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot create circular dependency in category hierarchy",
                )

        try:
            return await self.repo.update(category_id, data)
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )


    async def delete_category(self, category_id: int, force: bool = False):
        """Delete a category by ID with existence validation.

        Args:
            category_id: ID of the category to delete
            force: If True, delete category and all its subcategories

        Returns:
            None

        Raises:
            HTTPException: 404 if category doesn't exist
            HTTPException: 400 if category has children and force=False
        """

        category = await self.repo.get_by_id(category_id, include_children=True)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        if category.children and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with subcategories. Use force=True to delete all.",
            )

        products_count = await self.repo.get_products_count(category_id)
        if products_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {products_count} products. Move or delete products first.",
            )

        deleted = await self.repo.delete(category_id, force)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    async def get_products_count(
            self,
            category_id: int,
            include_subcategories: bool = False
    ) -> int:
        """Get count of products in a category.

        Args:
            category_id: ID of the category
            include_subcategories: Whether to include products from subcategories

        Returns:
            int: Number of products

        Raises:
            HTTPException: 404 if category not found
        """

        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        return await self.repo.get_products_count(category_id, include_subcategories)


    async def move_category(self, category_id: int, new_parent_id: Optional[int]):
        """Move a category to a new parent.

        Args:
            category_id: ID of the category to move
            new_parent_id: ID of new parent (None to make root)

        Returns:
            Category: Updated category

        Raises:
            HTTPException: 404 if category not found
            HTTPException: 400 if validation fails
        """
        update_data = CategoryUpdate(parent_id=new_parent_id, name=None)
        return await self.update_category(category_id, update_data)


    async def _would_create_cycle(self, category_id: int, parent_id: int) -> bool:
        """Check if moving category would create a circular dependency.

        Args:
            category_id: ID of the category being moved
            parent_id: Proposed new parent ID

        Returns:
            bool: True if would create cycle, False otherwise
        """

        descendants = await self.repo.get_all_descendants(category_id)
        descendant_ids = [d.id for d in descendants]

        return parent_id in descendant_ids
