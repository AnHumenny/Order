from typing import Optional, Any, Coroutine
from fastapi import UploadFile, HTTPException, status
from app.modules.products.gallery.repository import ProductImageRepository
from app.modules.products.gallery.schemas import ProductImageUpdate
from app.modules.products.gallery.upload import ImageUploadService


class ProductImageService:
    def __init__(self, image_repo: ProductImageRepository):
        self.image_repo = image_repo
        self.upload_service = ImageUploadService()


    async def upload_image(
        self,
        product_id: int,
        file: UploadFile,
        is_main: bool = False,
        alt_text: Optional[str] = None
    ):
        current_count = await self.image_repo.count_by_product(product_id)
        if current_count >= 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 7 images per product"
            )

        if is_main:
            await self.image_repo.unset_main_image(product_id)

        image_url, file_size, mime_type = await self.upload_service.save_image(
            file, product_id, is_main
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
        return await self.image_repo.get_by_product(product_id)


    async def update_image(
        self,
        image_id: int,
        product_id: int,
        update_data: ProductImageUpdate
    ):
        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return None

        if update_data.is_main is True:
            await self.image_repo.unset_main_image(product_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        return await self.image_repo.update(image_id, update_dict)


    async def delete_image(self, image_id: int, product_id: int) -> bool | None:
        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return False

        await self.upload_service.delete_image(image.image_url)
        return await self.image_repo.delete(image_id)


    async def set_as_main(self, image_id: int, product_id: int):
        image = await self.image_repo.get_by_id(image_id)
        if not image or image.product_id != product_id:
            return None

        await self.image_repo.unset_main_image(product_id)
        return await self.image_repo.update(image_id, {"is_main": True, "order": 0})
