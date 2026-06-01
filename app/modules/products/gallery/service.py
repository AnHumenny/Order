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
    def __init__(self, image_repo: ProductImageRepository,
                 product_repo: Optional[ProductRepository] = None):
        """Initialize ProductImageService with required repositories."""

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
        """Upload a new image for a product.

        Validates product existence, image limit (max 7), and handles main image logic.
        """

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
        """"Return all images for a specific product."""
        return await self.image_repo.get_by_product(product_id)


    async def get_image_by_id(self, image_id: int):
        """Return a single image by its ID."""
        return await self.image_repo.get_by_id(image_id)


    async def update_image(self, image_id: int, update_data: ProductImageUpdate):
        """Update image data by ID.

        If setting as main image, automatically unsets previous main image.
        """

        if update_data.is_main is True:
            current = await self.image_repo.get_by_id(image_id)
            if current:
                await self.image_repo.unset_main_image(current.product_id)

        update_dict = update_data.model_dump(exclude_unset=True)

        return await self.image_repo.update(image_id, update_dict)


    async def delete_image(self, image_id: int) -> dict:
        """Delete image from storage and database.

        Returns dict with success status and message.
        """

        image = await self.image_repo.get_by_id(image_id)
        if not image:
            return {"success": False, "message": f"Image {image_id} not found"}

        await self.upload_service.delete_image(image.image_url)

        return await self.image_repo.delete(image_id)


    async def set_as_main(self, image_id: int, product_id: int):
        """Set specified image as main for the product.

        Unsets previous main image. Returns updated image or None if invalid.
        """

        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return None

        await self.image_repo.unset_main_image(product_id)
        return await self.image_repo.update(image_id, {"is_main": True, "order": 0})
