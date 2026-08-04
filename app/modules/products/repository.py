import logging
import json
from typing import Optional, List, Tuple
from fastapi import HTTPException
from sqlalchemy import select, update, delete, func, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from app.modules.cart.models import CartItem
from app.modules.category.models import Category
from app.modules.orders.models import OrderItem
from app.modules.products.models import Product


class ProductRepository:
    """Repository for product-related database operations.

    Handles all data access for products including CRUD operations
    and business-specific queries like active product filtering.

    Args:
        session: SQLAlchemy async database session
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _normalize_description(product: Product) -> Product:
        """Normalizes product description."""

        if product.description:
            if isinstance(product.description, str):
                try:
                    product.description = json.loads(product.description)
                except json.JSONDecodeError:
                    product.description = {"main": product.description}
            elif isinstance(product.description, dict):
                default = {"main": "", "specs": "", "features": "", "reviews": ""}
                default.update(product.description)
                product.description = default
        return product


    def _normalize_products_list(self, products: List[Product]) -> List[Product]:
        """Normalizes the grocery list."""

        for product in products:
            self._normalize_description(product)
        return products


    async def get(self, product_id: int) -> Product | None:
        """Retrieve any product by ID, regardless of active status.

        Args:
            product_id: ID of the product to retrieve

        Returns:
            Product | None: Product if found, None otherwise
        """

        product = await self.session.get(Product, product_id)
        if product:
            self._normalize_description(product)
        return product


    async def get_active(self, product_id: int) -> Product | None:
        """Retrieve only active (available) product by ID.

        Args:
            product_id: ID of the product to retrieve

        Returns:
            Product | None: Active product if found, None otherwise
        """

        product = await self.session.scalar(
            select(Product)
            .where(
                Product.id == product_id,
                Product.is_active.is_(True),
            )
        )
        if product:
            self._normalize_description(product)
        return product


    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            include_inactive: bool = False
    ) -> list[Product]:
        """Retrieve products with optional inactive inclusion.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: If True, include inactive products

        Returns:
            list[Product]: List of products
        """

        query = select(Product).options(selectinload(Product.category))

        if not include_inactive:
            query = query.where(Product.is_active.is_(True))

        result = await self.session.scalars(
            query
            .offset(skip)
            .limit(limit)
            .order_by(Product.id.desc())
        )
        products = list(result)
        return self._normalize_products_list(products)


    async def get_product_by_id(self, product_id: int) -> Product:
        """Retrieve product by ID with category loaded.

        Args:
            product_id: ID of the product to retrieve

        Returns:
            Product: Product by id

        Raises:
            HTTPException: 404 if product not found
        """

        product = await self.session.scalar(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return self._normalize_description(product)


    async def create_with_category(self, product: Product) -> Product:
        """Create product and eagerly load category."""

        if product.description and isinstance(product.description, str):
            product.description = {
                "main": product.description,
                "specs": "",
                "features": "",
                "reviews": ""
            }

        self.session.add(product)
        await self.session.flush()

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product.id)
        )

        result = await self.session.execute(stmt)
        product = result.scalar_one()
        return self._normalize_description(product)


    async def deactivate(self, product_id: int) -> bool:
        """Deactivate (soft delete) a product.

        Sets is_active=False instead of hard deletion to preserve
        historical data in orders.

        Args:
            product_id: ID of the product to deactivate
        """

        result = await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(is_active=False)
            .returning(Product.id)
        )

        await self.session.commit()
        updated_count = len(result.fetchall())

        return updated_count > 0

    async def activate(self, product_id: int) -> bool:
        """Activate a product.

        Args:
            product_id: ID of the product to activate
        """

        result = await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(is_active=True)
            .returning(Product.id)
        )

        await self.session.commit()
        updated_count = len(result.fetchall())

        return updated_count > 0


    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""

        product = await self.session.get(Product, product_id)
        if product:
            self._normalize_description(product)
        return product


    async def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name."""
        query = select(Product).where(Product.name == name)
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        if product:
            self._normalize_description(product)
        return product


    async def check_category_exists(self, category_id: int) -> bool:
        """Check if category exists."""

        query = select(Category).where(Category.id == category_id)
        result = await self.session.execute(query)
        return result.first() is not None


    async def update(self, product_id: int, update_data: dict) -> Product:
        """Update product and return with category loaded."""

        if 'description' in update_data and update_data['description']:
            if isinstance(update_data['description'], str):
                try:
                    update_data['description'] = json.loads(update_data['description'])
                except json.JSONDecodeError:
                    update_data['description'] = {
                        "main": update_data['description'],
                        "specs": "",
                        "features": "",
                        "reviews": ""
                    }

        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        await self.session.flush()

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        result = await self.session.execute(stmt)
        product = result.scalar_one()
        return self._normalize_description(product)


    async def delete(self, product_id: int) -> bool:
        """Delete a product from the database by its ID.

        Args:
            product_id: ID of the product to delete

        Returns:
            bool: True if a product was deleted, False otherwise
        """

        product = await self.session.get(Product, product_id)
        if not product or product.is_active:
            return False

        result = await self.session.execute(
            delete(Product).where(Product.id == product_id)
        )

        await self.session.commit()

        if hasattr(result, 'rowcount'):
            return result.rowcount > 0
        return False


    async def can_delete_product(self, product_id: int) -> bool:
        """Check if product can be deleted (not in orders/carts)."""

        order_check = await self.session.execute(
            select(OrderItem).where(OrderItem.product_id == product_id).limit(1)
        )
        if order_check.first():
            return False

        cart_check = await self.session.execute(
            select(CartItem).where(CartItem.product_id == product_id).limit(1)
        )
        if cart_check.first():
            return False

        return True

    async def get_product_by_category(
            self,
            category_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> list[Product]:
        """Retrieve products from a specific category.

        Args:
            category_id: ID of the category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            list[Product]: List of products in the category
        """

        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.category_id == category_id)
            .where(Product.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(Product.id.desc())
        )
        products = list(result.scalars().all())
        return self._normalize_products_list(products)


    async def get_products_by_categories(
            self,
            category_ids: List[int],
            skip: int = 0,
            limit: int = 100
    ) -> list[Product]:
        """Retrieve products from multiple categories.

        Args:
            category_ids: List of category IDs
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            list[Product]: List of products from all specified categories
        """

        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.category_id.in_(category_ids))
            .where(Product.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(Product.id.desc())
        )
        products = list(result.scalars().all())
        return self._normalize_products_list(products)


    async def count_products_by_category(self, category_id: int) -> int:
        """Count active products in a specific category.

        Args:
            category_id: ID of the category

        Returns:
            int: Number of products
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.category_id == category_id)
            .where(Product.is_active.is_(True))
        )
        return result.scalar() or 0


    async def count_products_by_categories(self, category_ids: List[int]) -> int:
        """Count active products in multiple categories.

        Args:
            category_ids: List of category IDs

        Returns:
            int: Number of products
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.category_id.in_(category_ids))
            .where(Product.is_active.is_(True))
        )
        return result.scalar() or 0


    async def get_all_with_filters(
            self,
            search: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            category_ids: Optional[List[int]] = None,
            is_active: Optional[bool] = True,
            skip: int = 0,
            limit: int = 100
    ) -> List[dict]:
        """Return a list of products with filtering."""

        query = select(Product).options(
            selectinload(Product.category).selectinload(Category.parent)
        )

        if is_active is not None:
            query = query.where(Product.is_active == is_active)

        if search:
            query = query.where(
                Product.name.ilike(f"%{search}%")
            )

        if min_price is not None:
            query = query.where(Product.price >= min_price)

        if max_price is not None:
            query = query.where(Product.price <= max_price)

        if category_ids:
            query = query.where(Product.category_id.in_(category_ids))

        query = query.offset(skip).limit(limit).order_by(Product.id.desc())

        result = await self.session.execute(query)
        products = result.scalars().all()
        products = self._normalize_products_list(list(products))

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price) if p.price else None,
                "category_id": p.category_id,
                "category_name": p.category.name if p.category else None,
                "category_path": self._get_category_path_string(p.category) if p.category else None,
                "is_active": p.is_active
            }
            for p in products
        ]


    async def get_products_with_category_details(
            self,
            skip: int = 0,
            limit: int = 100,
            include_inactive: bool = False
    ) -> List[dict]:
        """Get products with full category hierarchy details."""

        query = select(Product).options(
            selectinload(Product.category)
            .selectinload(Category.parent)
        )

        if not include_inactive:
            query = query.where(Product.is_active.is_(True))

        query = query.offset(skip).limit(limit).order_by(Product.id.desc())

        result = await self.session.execute(query)
        products = result.scalars().all()
        products = self._normalize_products_list(list(products))

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price) if p.price else None,
                "category": {
                    "id": p.category.id,
                    "name": p.category.name,
                    "parent_id": p.category.parent_id,
                    "parent_name": p.category.parent.name if p.category.parent else None,
                    "level": self._get_category_level(p.category)
                } if p.category else None,
                "is_active": p.is_active
            }
            for p in products
        ]


    def _get_category_level(self, category: Category, current_level: int = 0) -> int:
        """Calculate category level in hierarchy."""

        if not category.parent:
            return current_level
        return self._get_category_level(category.parent, current_level + 1)


    @staticmethod
    def _get_category_path_string(category: Category) -> str:
        """Build category path string."""

        if not category:
            return ""

        path_parts = []
        current = category
        while current:
            path_parts.append(current.name)
            current = current.parent
        return " > ".join(reversed(path_parts))

    async def search_by_name(
            self,
            name: str,
            skip: int = 0,
            limit: int = 20,
            only_active: bool = True
    ) -> list[Product]:
        """Search products by name (case-insensitive partial match)."""

        try:
            query = select(Product).options(
                selectinload(Product.images),
                selectinload(Product.category)
            ).where(
                Product.name.ilike(f"%{name}%")
            )

            if only_active:
                query = query.where(Product.is_active)

            query = query.offset(skip).limit(limit)

            result = await self.session.execute(query)
            products = result.scalars().all()

            return self._normalize_products_list(list(products))

        except Exception as e:
            logging.error(f"ERROR in search_by_name: {e}")
            return []


    async def search_by_name_with_count(
            self,
            name: str,
            skip: int = 0,
            limit: int = 20,
            only_active: bool = True
    ) -> tuple[List[Product], int]:
        """Search products by name and return total count for pagination."""

        base_query = select(Product).options(
            selectinload(Product.images),
            selectinload(Product.category)
        ).where(
            Product.name.ilike(f"%{name}%")
        )

        if only_active:
            base_query = base_query.where(Product.is_active)

        count_query = select(func.count()).select_from(Product).where(
            Product.name.ilike(f"%{name}%")
        )

        if only_active:
            count_query = count_query.where(Product.is_active)

        total = await self.session.scalar(count_query) or 0

        query = base_query.offset(skip).limit(limit)
        result: Result = await self.session.execute(query)
        products_seq = result.scalars().all()

        products = self._normalize_products_list(list(products_seq))

        return products, total if total is not None else 0


    async def get_all_with_filters_and_count(
            self,
            search: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            category_ids: Optional[List[int]] = None,
            is_active: Optional[bool] = None,
            skip: int = 0,
            limit: int = 100
    ) -> Tuple[List[Product], int]:
        """Get products with filters and return total count."""

        query = select(Product).options(selectinload(Product.category))

        if search:
            query = query.where(
                Product.name.ilike(f"%{search}%")
            )

        if min_price is not None:
            query = query.where(Product.price >= min_price)

        if max_price is not None:
            query = query.where(Product.price <= max_price)

        if category_ids:
            query = query.where(Product.category_id.in_(category_ids))

        if is_active is not None:
            query = query.where(Product.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        result = await self.session.execute(
            query.offset(skip).limit(limit)
        )
        products = result.scalars().all()

        return self._normalize_products_list(list(products)), total


    async def update_description_section(
            self,
            product_id: int,
            section: str,
            content: str
    ) -> Product:
        """Update a specific section of the product description."""

        product = await self.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if not product.description or not isinstance(product.description, dict):
            product.description = {
                "main": "",
                "specs": "",
                "features": "",
                "reviews": ""
            }

        product.description[section] = content

        await self.session.commit()
        await self.session.refresh(product)

        return self._normalize_description(product)
