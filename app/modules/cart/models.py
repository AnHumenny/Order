from sqlalchemy import ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime
from datetime import datetime

from app.core.database import Base
from app.modules.products.models import Product


class Cart(Base):
    """Shopping cart model representing a user's cart.

    Each user has exactly one cart containing multiple items.

    Attributes:
        user_id: Reference to the cart owner (foreign key to users.id)
        created_at: Timestamp when cart was created
        items: List of items in the cart (relationship to CartItem)
    """
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        cascade="all, delete-orphan",
        back_populates="cart"
    )


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

    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart: Mapped["Cart"] = relationship(
        "Cart",
        back_populates="items"
    )

    product: Mapped[Product] = relationship(
        Product,
        lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )
