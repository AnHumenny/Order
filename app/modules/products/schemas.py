from typing import Optional
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from app.modules.category.schemas import CategoryRead


class ProductCreate(BaseModel):
    """Schema for creating a new product.

    Used in POST requests to create products. All fields except description are required.

    Attributes:
        name: Product display name
        description: Optional detailed description
        price: Product price
    """
    name: str
    category: str | None = None
    description: str | None = None
    price: Decimal


class ProductRead(BaseModel):
    """Schema for reading product information.

    Used in responses when returning product data. Includes ID and all product details.

    Attributes:
        id: Product identifier
        description: Optional detailed description
        price: Product price
    """
    id: int
    category: Optional[CategoryRead] = None
    name: str
    description: str | None = None
    price: Decimal
    category_id: Optional[int] = None


    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    """Schema for updating existing products.

    Used in PATCH requests. All fields are optional - only provided fields are updated.

    Attributes:
        name: New product name (if provided)
        description: New description (if provided)
        price: New price (if provided)
        is_active: New active status (if provided)
    """
    name: str | None = None
    category: str
    description: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None
