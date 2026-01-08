from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderItem, OrderStatus
from app.modules.cart.repository import CartRepository
from app.modules.payment.stripe_client import create_payment_intent # пока оставим


from decimal import Decimal
from fastapi import HTTPException

class OrderService:
    """Service layer for order business logic."""

    def __init__(self, order_repo, cart_repo):
        self.order_repo = order_repo
        self.cart_repo = cart_repo

    async def create_from_cart(self, user_id: int) -> Order:
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
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .where(Order.status == OrderStatus.PENDING)
    )
    return result.scalar_one_or_none()


async def checkout_cart(db: AsyncSession, user) -> dict:
    """Creates an order for the current user from the shopping cart.

    If there is already an order with the PENDING status, it returns it.
    """

    result = await db.execute(
        select(Order)
        .where(Order.user_id == user.id)
        .where(Order.status == OrderStatus.PENDING)
    )
    pending_order = result.scalar_one_or_none()

    if pending_order:
        return {
            "order_id": pending_order.id,
            "status": pending_order.status,
            "total_amount": pending_order.total_amount,
        }


    cart_repo = CartRepository(db)
    cart_service = CartService(cart_repo)
    cart_items = await cart_service.get_cart_items_for_checkout(user.id)

    if not cart_items:
        raise HTTPException(400, "Cart is empty")

    total_amount = sum(
        Decimal(item.product.price) * item.quantity for item in cart_items
    )

    order = Order(
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        stripe_payment_intent_id=None,
    )
    db.add(order)
    await db.flush()

    order_items = [
        OrderItem(
            order_id=order.id,
            product_id=item.product.id,
            product_name=item.product.name,
            price=Decimal(item.product.price),
            quantity=item.quantity,
        )
        for item in cart_items
    ]
    db.add_all(order_items)

    # await cart_service.clear_cart(user.id)

    await db.commit()

    return {
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
    }
