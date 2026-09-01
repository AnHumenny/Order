from typing import List, Optional, cast
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.category.models import Category
from app.modules.category.schemas import CategoryCreate, CategoryUpdate
from app.modules.products.models import Product


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
            get_by_name: Retrieve a category by its name
            get_root_categories: Retrieve all root categories (no parent)
            get_children: Retrieve direct subcategories of a category
            get_all_descendants: Retrieve all descendants of a category
            get_category_tree: Retrieve full category tree
            get_category_path: Retrieve path from root to category
            update: Update a category
            delete: Remove a category from the database
            get_products_count: Get count of products in a category
            check_products_exist: Check if category has any products
        """

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, name: str, parent_id: Optional[int] = None) -> Category:
        """Create and persist a new category in the database.

        Args:
            name: Name of the new category
            parent_id: Optional ID of parent category

        Returns:
            Category: The newly created Category instance with generated ID
        """

        category = Category(name=name, parent_id=parent_id)
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category


    async def create_from_schema(self, data: CategoryCreate) -> Category:
        """Create a new category from Pydantic schema.

        Args:
            data: CategoryCreate schema with name and parent_id

        Returns:
            Category: The newly created Category instance
        """
        return await self.create(data.name, data.parent_id)


    async def get_all(self, skip: int = 0, limit: int = 100, include_hierarchy: bool = False) -> list[Category]:
        """Retrieve all categories from the database.

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            include_hierarchy: Whether to load parent and children relationships

        Returns:
            list[Category]: List of all categories, ordered by ID descending
        """

        query = select(Category).offset(skip).limit(limit).order_by(Category.id.desc())

        if include_hierarchy:
            query = query.options(
                selectinload(Category.parent),
                selectinload(Category.children)
            )

        result = await self.session.execute(query)
        return list(result.scalars())


    async def get_by_id(
            self,
            category_id: int,
            include_children: bool = False
    ) -> Category | None:
        """Retrieve a category by its unique identifier."""

        query = select(Category).where(Category.id == category_id)

        if include_children:
            query = query.options(selectinload(Category.children))

        category = await self.session.scalar(query)

        return cast(Category | None, category)


    async def get_by_name(self, name: str) -> Category | None:
        """Retrieve a category by its name."""

        category = await self.session.scalar(
            select(Category).where(Category.name == name)
        )

        return cast(Category | None, category)


    async def get_root_categories(self) -> list[Category]:
        """Retrieve all root categories (categories without a parent).

        Returns:
            list[Category]: List of root categories
        """

        result = await self.session.execute(
            select(Category)
            .where(Category.parent_id.is_(None))
            .options(selectinload(Category.children))
            .order_by(Category.name)
        )
        return list(result.scalars().all())


    async def get_children(self, category_id: int) -> list[Category]:
        """Retrieve direct subcategories of a category.

        Args:
            category_id: ID of the parent category

        Returns:
            list[Category]: List of direct subcategories
        """

        result = await self.session.execute(
            select(Category)
            .where(Category.parent_id == category_id)
            .order_by(Category.name)
        )
        return list(result.scalars().all())


    async def get_all_descendants(self, category_id: int) -> list[Category]:
        """Retrieve all descendants of a category (recursive).

        Args:
            category_id: ID of the parent category

        Returns:
            list[Category]: List of all descendant categories
        """

        cte = (
            select(Category)
            .where(Category.id == category_id)
            .cte(name="descendants", recursive=True)
        )

        cte = cte.union_all(
            select(Category)
            .join(cte, Category.parent_id == cte.c.id)
        )

        result = await self.session.execute(
            select(Category).from_statement(
                select(cte).where(cte.c.id != category_id)
            )
        )
        return list(result.scalars().all())

    async def get_category_tree(self, category_id: int, max_depth: Optional[int] = None):
        """Retrieve full category tree starting from a category.

        Args:
            category_id: ID of the root category for the tree
            max_depth: Maximum depth of the tree (optional)

        Returns:
            Category: Category with all children loaded recursively
        """

        category = await self.get_by_id(category_id, include_children=True)
        if category:
            await self._load_children_recursive(category, max_depth)
        return category


    async def _load_children_recursive(self, category: Category, max_depth: Optional[int] = None,
                                       current_depth: int = 0):
        """Recursively load children for a category.

        Args:
            category: Category object to load children for
            max_depth: Maximum depth to load
            current_depth: Current recursion depth
        """

        if max_depth is not None and current_depth >= max_depth:
            return

        await self.session.refresh(category, ['children'])

        for child in category.children:
            await self._load_children_recursive(child, max_depth, current_depth + 1)


    async def get_category_path(self, category_id: int) -> list[Category]:
        """Retrieve path from root to category.

        Args:
            category_id: ID of the category

        Returns:
            list[Category]: List of categories from root to target
        """

        path = []
        current = await self.get_by_id(category_id)

        while current:
            path.append(current)
            if current.parent_id:
                current = await self.get_by_id(current.parent_id)
            else:
                current = None

        return list(reversed(path))


    async def update(self, category_id: int, data: CategoryUpdate) -> Category | None:
        """Update a category.

        Args:
            category_id: ID of the category to update
            data: Update data (name, parent_id)

        Returns:
            Category | None: Updated category if found, None otherwise
        """

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(category_id)

        await self.session.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(**update_data)
        )
        await self.session.flush()

        return await self.get_by_id(category_id)


    async def delete(self, category_id: int, force: bool = False) -> bool:
        """Delete a category from the database by its ID.

        Args:
            category_id: ID of the category to delete
            force: If True, delete category and all its subcategories

        Returns:
            bool: True if a category was deleted, False if no category with given ID exists
        """

        if force:
            descendants = await self.get_all_descendants(category_id)
            descendant_ids = [d.id for d in descendants] + [category_id]

            result = await self.session.execute(
                delete(Category).where(Category.id.in_(descendant_ids))
            )
        else:
            children = await self.get_children(category_id)
            if children:
                return False

            result = await self.session.execute(
                delete(Category).where(Category.id == category_id)
            )

        if hasattr(result, 'rowcount'):
            return True
        return False


    async def get_products_count(self, category_id: int, include_subcategories: bool = False) -> int:
        """Get count of products in a category.

        Args:
            category_id: ID of the category
            include_subcategories: Whether to include products from subcategories

        Returns:
            int: Number of products
        """

        if include_subcategories:
            descendants = await self.get_all_descendants(category_id)
            category_ids = [d.id for d in descendants] + [category_id]

            result = await self.session.execute(
                select(func.count())
                .select_from(Product)
                .where(Product.category_id.in_(category_ids))
                .where(Product.is_active)
            )
        else:
            result = await self.session.execute(
                select(func.count())
                .select_from(Product)
                .where(Product.category_id == category_id)
                .where(Product.is_active)
            )

        return result.scalar() or 0


    async def check_products_exist(self, category_id: int) -> bool:
        """Check if category has any products.

        Args:
            category_id: ID of the category

        Returns:
            bool: True if category has products, False otherwise
        """

        result = await self.session.execute(
            select(Product.id)
            .where(Product.category_id == category_id)
            .limit(1)
        )
        return result.first() is not None


    async def get_category_tree_ids(self, category_id: int) -> List[int]:
        """Get all category IDs in the tree starting from the given category.

        This includes the category itself and all its subcategories at any depth.

        Args:
            category_id: ID of the root category

        Returns:
            List[int]: List of all category IDs in the tree
        """

        cte = (
            select(Category.id, Category.parent_id)
            .where(Category.id == category_id)
            .cte(name="category_tree", recursive=True)
        )

        cte = cte.union_all(
            select(Category.id, Category.parent_id)
            .join(cte, Category.parent_id == cte.c.id)
        )

        result = await self.session.execute(
            select(cte.c.id)
        )
        return [row[0] for row in result]


    async def get_root_categories_with_full_tree(self) -> list[Category]:
        """Get all root categories with all descendants loaded recursively."""

        result = await self.session.execute(
            select(Category)
            .where(Category.parent_id.is_(None))
            .order_by(Category.name)
        )
        roots = list(result.scalars().all())

        for root in roots:
            await self._load_all_children(root)

        return roots


    async def _load_all_children(self, category: Category, max_depth: Optional[int] = None, current_depth: int = 0):
        """Recursively load all children for a category."""

        if max_depth is not None and current_depth >= max_depth:
            return

        await self.session.refresh(category, ['children'])

        for child in category.children:
            await self._load_all_children(child, max_depth, current_depth + 1)
