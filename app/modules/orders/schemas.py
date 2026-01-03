from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class OrderItemRead(BaseModel):
    """Schema for reading order item information.

    Represents a product within an order. Contains historical data
    (price, product name) as it was at the time of purchase.

    Attributes:
        product_id: ID of the purchased product
        product_name: Product name at time of purchase
        price: Price per unit at time of purchase
        quantity: Number of units purchased
    """
    product_id: int
    product_name: str
    price: Decimal
    quantity: int

    class Config:
        """Pydantic configuration for ORM compatibility."""
        from_attributes = True


class OrderRead(BaseModel):
    """Schema for reading complete order information.

    Contains order metadata and all items with calculated total price.
    Used for order confirmation and order history display.

    Attributes:
        id: Unique order identifier
        status: Current order status
        created_at: When the order was placed
        items: List of products in the order
        total_price: Total cost of the order
    """
    id: int
    status: str
    created_at: datetime
    items: list[OrderItemRead]
    total_price: Decimal

    class Config:
        """Pydantic configuration for ORM compatibility."""
        from_attributes = True
