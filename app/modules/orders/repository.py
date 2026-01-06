from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.orders.models import Order, OrderItem
from sqlalchemy.orm import Session


def create_order(db: Session, order: Order) -> Order:
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def add_order_items(db: Session, items: list[OrderItem]) -> None:
    db.add_all(items)
    db.commit()


def get_order_by_id(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


class OrderRepository:
    """Repository for order-related database operations.

    Handles all data access for orders and order items.
    Provides methods for creating and retrieving orders.

    Args:
        session: SQLAlchemy async database session
    """
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, order: Order) -> Order:
        """Create a new order in the database.

        Persists an order and its associated items.
        Used when converting a cart to an order.

        Args:
            order: Order instance with items populated

        Returns:
            Order: The created order with ID assigned
        """

        self.session.add(order)
        await self.session.flush()
        return order


    async def get_by_user(self, user_id: int) -> list[Order]:
        """Retrieve all orders placed by a specific user.

        Args:
            user_id: ID of the user whose orders to retrieve

        Returns:
            list[Order]: List of user's orders, possibly empty
        """

        result = await self.session.scalars(
            select(Order).where(Order.user_id == user_id)
        )
        return list(result)
