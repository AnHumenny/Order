from typing import Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.products.gallery import ProductImageUpdate
from app.modules.products.gallery.models import ProductImage


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


    async def get_by_id(self, image_id: int) -> Optional[ProductImage]:
        """Get image by ID."""
        result = await self.session.execute(
            select(ProductImage).where(ProductImage.id == image_id)
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


    async def update(
            self,
            image_id: int,
            update_data: dict,
    ) -> Optional[ProductImageUpdate]:
        """Update an image by ID with provided data."""

        await self.session.execute(
            update(ProductImage)
            .where(ProductImage.id == image_id)
            .values(**update_data)
        )
        await self.session.flush()

        product_image = await self.get_by_id(image_id)
        if not product_image:
            return None

        return ProductImageUpdate.model_validate(product_image)


    async def delete(self, image_id: int) -> dict:
        """Delete image by ID. Returns dict with success status and message."""

        result = await self.session.execute(
            delete(ProductImage).where(ProductImage.id == image_id)
        )
        await self.session.flush()

        if result.rowcount > 0:  # type: ignore[attr-defined]
            return {"success": True, "message": f"Image {image_id} deleted successfully"}
        else:
            return {"success": False, "message": f"Image {image_id} not found"}


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
