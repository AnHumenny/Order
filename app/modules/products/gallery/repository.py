from typing import Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.products import Product
from app.modules.products.gallery.models import ProductImage
from sqlalchemy.orm import selectinload


class ProductImageRepository:
    """Repository for product image database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, image_data: dict) -> ProductImage:
        """Create a new product image record."""

        db_image = ProductImage(**image_data)
        self.session.add(db_image)
        await self.session.flush()
        await self.session.refresh(db_image)
        return db_image


    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get image by id"""

        result = await self.session.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.category))
        )
        return result.scalar_one_or_none()


    async def get_by_product(self, product_id: int) -> Sequence[ProductImage]:
        """Get all images for a product, ordered by order field."""

        result = await self.session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.order)
        )
        return result.scalars().all()


    async def update(self, image_id: int, update_data: dict) -> Optional[ProductImage]:
        """Update an image by ID with provided data."""

        await self.session.execute(
            update(ProductImage)
            .where(ProductImage.id == image_id)
            .values(**update_data)
        )
        await self.session.flush()
        return await self.get_by_id(image_id)


    async def delete(self, image_id: int) -> None:
        """Delete image."""

        await self.session.execute(
            delete(ProductImage).where(ProductImage.id == image_id)
        )
        await self.session.flush()


    async def unset_main_image(self, product_id: int) -> None:
        """Unset main image flag for all images of a product."""

        await self.session.execute(
            update(ProductImage)
            .where(ProductImage.product_id == product_id)
            .values(is_main=False)
        )
        await self.session.flush()


    async def count_by_product(self, product_id: int) -> int:
        """Count number of images for a product."""

        result = await self.session.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        return len(result.scalars().all())
