from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderItem, OrderStatus
from app.modules.cart.repository import CartRepository
from decimal import Decimal
from fastapi import HTTPException
from app.modules.products.models import Product


class OrderService:
    """Service layer for order business logic."""

    def __init__(self, order_repo, cart_repo):
        self.order_repo = order_repo
        self.cart_repo = cart_repo


    async def create_from_cart(self, user_id: int) -> Order:
        """Create an order from the user's shopping cart.

        Converts the user's cart into a new order by:
        1. Retrieving the user's cart with all items
        2. Validating the cart is not empty
        3. Calculating the total order amount
        4. Creating an Order with PENDING status
        5. Converting cart items to order items
        6. Persisting the order to the database
        """

        cart = await self.cart_repo.get_cart_with_items(user_id)

        if not cart or not cart.items:
            raise HTTPException(400, "Cart is empty")

        total_amount = sum(Decimal(item.product.price) * item.quantity for item in cart.items)

        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
        )

        order_items = []
        for item in cart.items:
            order_item = OrderItem(
                product_id=item.product_id,
                product_name=item.product.name,
                price=Decimal(item.product.price),
                quantity=item.quantity,
            )
            order_items.append(order_item)

        order.items.extend(order_items)

        await self.order_repo.create(order)

        return order


def calculate_order_total(items: list[OrderItem]) -> int:
    """Returns the order amount in minimum units (cents)."""

    total = 0
    for item in items:
        total += int(item.price * 100) * item.quantity
    return total


async def get_pending_order(db: AsyncSession, user_id: int):
    """Retrieve a pending order for a specific user.

    Queries the database for an order with PENDING status belonging to
    the given user. Returns the order if found, otherwise returns None.
    """

    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .where(Order.status == OrderStatus.PENDING)
    )
    return result.scalar_one_or_none()


async def checkout_cart(db: AsyncSession, user) -> dict:
    """Hard recalculation of the basket: delete the old order, create a new one with up-to-date data"""

    result = await db.execute(
        select(Order).where(
            Order.user_id == user.id,
            Order.status == OrderStatus.PENDING
        )
    )
    old_orders = result.scalars().all()

    for old_order in old_orders:
        await db.delete(old_order)
    await db.flush()

    cart_service = CartService(CartRepository(db))
    cart = await cart_service.get_cart(user.id)

    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty")

    now = datetime.now(timezone.utc)
    new_order = Order(
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_amount=Decimal("0.00"),
        expires_at=now + timedelta(minutes=10),
    )
    db.add(new_order)
    await db.flush()

    total_amount = Decimal("0.00")

    for cart_item in cart.items:
        product = await db.get(Product, cart_item.product_id)
        if not product:
            raise HTTPException(400, f"Product {cart_item.product_id} not found")

        current_price = product.price
        current_quantity = cart_item.quantity
        subtotal = current_price * current_quantity

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            product_name=product.name,
            price=current_price,
            quantity=current_quantity
        )
        db.add(order_item)
        total_amount += subtotal

    new_order.total_amount = total_amount
    await db.commit()

    return {
        "order_id": new_order.id,
        "amount": float(new_order.total_amount),
        "currency": "EUR",
        "expires_at": new_order.expires_at.isoformat() if new_order.expires_at else None,
    }
