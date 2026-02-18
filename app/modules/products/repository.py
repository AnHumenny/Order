from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
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


    async def get(self, product_id: int) -> Product | None:
        """Retrieve any product by ID, regardless of active status.

        Args:
            product_id: ID of the product to retrieve

        Returns:
            Product | None: Product if found, None otherwise
        """
        return await self.session.get(Product, product_id)

    async def get_active(self, product_id: int) -> Product | None:
        """Retrieve only active (available) product by ID.

        Args:
            product_id: ID of the product to retrieve

        Returns:
            Product | None: Active product if found, None otherwise
        """

        return await self.session.scalar(
            select(Product)
            .where(
                Product.id == product_id,
                Product.is_active.is_(True),
            )
        )


    async def get_all(self, skip, limit) -> list[Product]:
        """Retrieve all active products ordered by ID.

        Returns:
            list[Product]: List of active products
        """

        result = await self.session.scalars(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(Product.id)
        )
        return list(result)



    async def get_product_by_id(self, product_id) -> Product:
        """Retrieve all active products ordered by ID.

        Returns:
            Product by id
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

        return product


    async def create_with_category(self, product: Product) -> Product:
        """Create product and eagerly load category."""
        self.session.add(product)
        await self.session.flush()

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product.id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def update(self, product: Product) -> Product:
        """Update an existing product.

        Args:
            product: Modified product instance

        Returns:
            Product: Updated product
        """

        await self.session.flush()
        return product


    async def deactivate(self, product_id: int) -> None:
        """Deactivate (soft delete) a product.

        Sets is_active=False instead of hard deletion to preserve
        historical data in orders.

        Args:
            product_id: ID of the product to deactivate
        """

        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(is_active=False)
        )


    async def delete(self, product_id: int) -> bool:
        """Delete a product from the database by its ID.

        Args:
            product_id: ID of the product to delete

        Returns:
            bool: True if a product was deleted, False if no product with given ID exists
        """

        result = await self.session.execute(
            delete(Product).where(Product.id == product_id)
        )

        if hasattr(result, 'rowcount'):
            return result.rowcount > 0
        return False


    async def get_product_by_category(self, category_id, skip, limit) -> list[Product]:
        """Retrieve all active products ordered by ID.

        Returns:
            Product by id
        """

        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .order_by(Product.id)
        )

        return list(result.scalars().all())
