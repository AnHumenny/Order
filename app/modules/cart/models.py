from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime
from datetime import datetime
from app.modules.products.models import Product


class Base(DeclarativeBase):
    """The base class for all models.

    Attributes:
        id (int): Primary key, unique identifier for the record.
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Cart(Base):
    """Shopping cart model representing a user's cart.

    Each user has exactly one cart containing multiple items.

    Attributes:
        user_id: Reference to the cart owner (foreign key to users.id)
        created_at: Timestamp when cart was created
        items: List of items in the cart (relationship to CartItem)
    """
    __tablename__ = "carts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    items: Mapped[list["CartItem"]] = relationship("CartItem", cascade="all, delete-orphan")


class CartItem(Base):
    """Individual item within a shopping cart.

    Represents a product added to a cart with its quantity.

    Attributes:
        cart_id: Reference to the parent cart (foreign key to carts.id)
        product_id: Reference to the product (foreign key to products.id)
        quantity: Number of this product in the cart
        product: Relationship to the Product model
    """
    __tablename__ = "cart_items"

    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    product: Mapped["Product"] = relationship("Product")
