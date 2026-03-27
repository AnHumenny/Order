from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductImageBase(BaseModel):
    """Base schema for product image data."""

    image_url: str = Field(..., max_length=500)
    alt_text: Optional[str] = Field(None, max_length=200)
    is_main: bool = Field(False)
    order: int = Field(0, ge=0, le=6)


class ProductImageCreate(ProductImageBase):
    """Schema for creating a new product image."""

    product_id: int
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class ProductImageUpdate(BaseModel):
    """Schema for updating an existing product image."""

    image_url: Optional[str] = Field(None, max_length=500)
    alt_text: Optional[str] = Field(None, max_length=200)
    is_main: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0, le=6)


class ProductImageRead(ProductImageBase):
    """Schema for reading product image data."""

    id: int
    product_id: int
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
