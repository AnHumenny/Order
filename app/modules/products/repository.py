from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
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


    async def list(self) -> list[Product]:
        """Retrieve all active products ordered by ID.

        Returns:
            list[Product]: List of active products
        """

        result = await self.session.scalars(
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.id)
        )
        return list(result)


    async def create(self, product: Product) -> Product:
        """Create a new product.

        Args:
            product: Product instance to persist

        Returns:
            Product: Created product with ID assigned
        """

        self.session.add(product)
        await self.session.flush()
        return product


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
