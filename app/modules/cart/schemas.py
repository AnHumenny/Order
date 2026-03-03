from decimal import Decimal
from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    """Schema for adding a new item to the cart.

    Used in POST requests to specify which product and how many to add.

    Attributes:
        product_id: ID of the product to add to cart
        quantity: Number of units to add (must be greater than 0)
    """
    product_id: int
    quantity: int = Field(gt=0)


class CartItemRead(BaseModel):
    """Schema for reading cart item information.

    Returned when reading cart contents. Includes product details.

    Attributes:
        product_id: ID of the product
        product_name: Name of the product
        price: Current price of the product
        quantity: Quantity of this product in the cart
    """
    product_id: int
    product_name: str
    price: Decimal
    quantity: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CartRead(BaseModel):
    """Schema for reading full cart information.

    Returned when retrieving the user's cart. Contains all items and total price.

    Attributes:
        items: List of all items in the cart
        total_price: Total price of all items in the cart
    """

    items: list[CartItemRead]
    total_price: Decimal

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., ge=1, description="New quantity (must be >= 1)")
