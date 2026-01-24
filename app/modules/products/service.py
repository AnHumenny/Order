from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate


class ProductService:

    def __init__(self, repo: ProductRepository):
        self.repo = repo

    @staticmethod
    async def create_product(
        *,
        data: ProductCreate,
        session: AsyncSession,
    ) -> Product:
        """Create product."""
        product_data = data.model_dump()
        product_data.pop("category", None)
        product = Product(**product_data)

        session.add(product)
        await session.commit()

        await session.refresh(product)

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product.id)
        )

        result = await session.execute(stmt)
        return result.scalar_one()


    @staticmethod
    async def list_products(
            *,
            session: AsyncSession,
            skip: int = 0,
            limit: int = 100,
    ) -> list[Product]:
        """Get list of all products."""

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .offset(skip)
            .limit(limit)
            .order_by(Product.id)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())


    @staticmethod
    async def get_product_by_id(
            *,
            product_id: int,
            session: AsyncSession,
    ) -> Product:
        """Get single product by id."""

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )

        result = await session.execute(stmt)
        product = result.scalar_one_or_none()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return product


    async def delete_product(self, category_id: int):
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
                detail="Product not found",
            )

    @staticmethod
    async def list_category_products(
            *,
            session: AsyncSession,
            category_id: int,
            skip: int = 0,
            limit: int = 10,
    ) -> list[Product]:
        """Get all products from selected categories."""

        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .order_by(Product.id)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())
