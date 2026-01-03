from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    """Order model representing a completed purchase.

    Stores order metadata, status, and relationship to user.
    Contains multiple order items (products purchased).

    Attributes:
        id: Unique order identifier
        user_id: Customer who placed the order (foreign key to users.id)
        status: Current order status (e.g., "created", "paid", "shipped")
        created_at: Timestamp when order was placed
        items: List of products in this order (relationship to OrderItem)
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="created",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    """Individual product within an order.

    Represents a snapshot of a product at the time of purchase.
    Stores product details to preserve historical data even if product changes.

    Attributes:
        id: Unique order item identifier
        order_id: Parent order (foreign key to orders.id)
        product_id: Original product ID
        product_name: Product name at time of purchase
        price: Price per unit at time of purchase
        quantity: Number of units purchased
        order: Relationship back to parent Order
    """
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(nullable=False)

    order = relationship("Order", back_populates="items")
