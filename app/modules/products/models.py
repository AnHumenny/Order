from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from ..category.models import Category


class Product(Base):
    """Product model representing items available for purchase.

    Stores product information including pricing and availability status.
    Products can be added to carts and purchased in orders.

    Attributes:
        id: Unique product identifier
        name: Product display name
        description: Detailed product description
        price: Current price (decimal with 2 places)
        is_active: Whether product is available for purchase
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category: Mapped[Optional["Category"]] = relationship(
        back_populates="products"
    )


    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f"<Product id={self.id} name={self.name}>"
