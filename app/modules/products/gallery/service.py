from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from app.modules.category.models import Category
from app.modules.products import Product
from app.modules.products.gallery.repository import ProductImageRepository
from app.modules.products.gallery.schemas import ProductImageUpdate
from app.modules.products.gallery.upload import ImageUploadService
from app.modules.products.repository import ProductRepository


class ProductImageService:
    """Service for managing product images with upload, update, and deletion."""

    def __init__(self, image_repo: ProductImageRepository, product_repo: ProductRepository):
        self.image_repo = image_repo
        self.product_repo = product_repo
        self.upload_service = ImageUploadService()

    async def upload_image(
            self,
            product_id: int,
            file: UploadFile,
            is_main: bool = False,
            alt_text: Optional[str] = None
    ):
        """  """

        result = await self.image_repo.session.execute(
            select(Product.category_id, Category.name)
            .select_from(Product)
            .join(Category, Product.category_id == Category.id, isouter=True)
            .where(Product.id == product_id)
        )
        row = result.first()

        if not row:
            raise HTTPException(status_code=404, detail="Product not found")

        category_id = row[0]
        category_name = row[1]

        current_count = await self.image_repo.count_by_product(product_id)
        if current_count >= 7:
            raise HTTPException(400, "Maximum 7 images per product")

        if is_main:
            await self.image_repo.unset_main_image(product_id)

        image_url, file_size, mime_type = await self.upload_service.save_image(
            file=file,
            product_id=product_id,
            category_id=category_id,
            category_name=category_name,
            is_main=is_main
        )

        image_data = {
            "image_url": image_url,
            "alt_text": alt_text,
            "is_main": is_main,
            "order": current_count,
            "product_id": product_id,
            "file_size": file_size,
            "mime_type": mime_type
        }

        return await self.image_repo.create(image_data)


    async def get_product_images(self, product_id: int):
        """Get all images for a product."""
        return await self.image_repo.get_by_product(product_id)


    async def update_image(
        self,
        image_id: int,
        product_id: int,
        update_data: ProductImageUpdate
    ):
        """Update an existing product image."""

        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return None

        if update_data.is_main is True:
            await self.image_repo.unset_main_image(product_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        return await self.image_repo.update(image_id, update_dict)


    async def delete_image(self, image_id: int, product_id: int) -> bool | None:
        """Delete a product image and its file from storage."""

        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return False

        await self.upload_service.delete_image(str(image.image_url))
        return await self.image_repo.delete(image_id)


    async def set_as_main(self, image_id: int, product_id: int):
        """Set an image as the main image for a product."""

        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return None

        await self.image_repo.unset_main_image(product_id)
        return await self.image_repo.update(image_id, {"is_main": True, "order": 0})
