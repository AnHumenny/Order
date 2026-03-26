from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_admin
from app.modules.products.gallery.repository import ProductImageRepository
from app.modules.products.gallery.service import ProductImageService
from app.modules.products.gallery.schemas import ProductImageRead, ProductImageUpdate

router = APIRouter(
    prefix="/products/{product_id}/images"
)


@router.get("/", response_model=List[ProductImageRead])
async def get_product_images(
        product_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Get all images for a product."""

    repo = ProductImageRepository(session)
    service = ProductImageService(repo)
    return await service.get_product_images(product_id)


@router.post("/upload", response_model=ProductImageRead, status_code=status.HTTP_201_CREATED) # добавить thumbnails
async def upload_product_image(
        product_id: int,
        file: UploadFile = File(...),
        is_main: bool = Form(False),
        alt_text: Optional[str] = Form(None),
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin)
):
    """Upload a new image for a product. Max 7 images per product, max 5MB."""

    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, WEBP and GIF images are allowed"
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )
    await file.seek(0)

    repo = ProductImageRepository(session)
    service = ProductImageService(repo)

    image = await service.upload_image(product_id, file, is_main, alt_text)
    await session.commit()
    return image


@router.patch("/{image_id}", response_model=ProductImageRead)
async def update_product_image(
        product_id: int,
        image_id: int,
        image_data: ProductImageUpdate,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin)
):
    """Update an existing product image."""

    repo = ProductImageRepository(session)
    service = ProductImageService(repo)

    updated = await service.update_image(image_id, product_id, image_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Image not found")

    await session.commit()
    return updated


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
        product_id: int,
        image_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin)
):
    """Delete a product image and remove its file from storage."""

    repo = ProductImageRepository(session)
    service = ProductImageService(repo)

    deleted = await service.delete_image(image_id, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Image not found")

    await session.commit()


@router.post("/{image_id}/set-main", response_model=ProductImageRead)
async def set_main_image(
        product_id: int,
        image_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin)
):
    """Set an image as the main image for the product."""

    repo = ProductImageRepository(session)
    service = ProductImageService(repo)

    updated = await service.set_as_main(image_id, product_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Image not found")

    await session.commit()
    return updated
