from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class ProductCreate(BaseModel):
    """Schema for creating a new product.

    Used in POST requests to create products. All fields except description are required.

    Attributes:
        name: Product display name
        description: Optional detailed description
        price: Product price
    """
    name: str
    description: str | None = None
    price: Decimal


class ProductRead(BaseModel):
    """Schema for reading product information.

    Used in responses when returning product data. Includes ID and all product details.

    Attributes:
        id: Product identifier
        name: Product display name
        description: Optional detailed description
        price: Product price
    """
    id: int
    name: str
    description: str | None = None
    price: Decimal

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
    description: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None
