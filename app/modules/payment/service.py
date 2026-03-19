from datetime import datetime, timezone, timedelta
from decimal import Decimal
import stripe
from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderStatus, OrderItem
from app.modules.products.models import Product


async def handle_stripe_webhook(event: dict, session: AsyncSession) -> dict:
    """Process Stripe webhook events and update order status accordingly.

    Handles Stripe webhook events, specifically processing checkout.session.completed
    events to mark orders as paid and clear the user's cart.

    Args:
        event: Stripe event object containing event type and data
        session: Async database session for updating order status

    Returns:
        dict: Processing status with one of the following:
            - {"status": "ignored"}: For non-checkout events
            - {"status": "order not found"}: If order cannot be located
            - {"status": "already paid"}: If order is already in PAID status
            - {"status": "ok"}: If order successfully updated to PAID status

    Raises:
        SQLAlchemyError: If database operation fail
    """

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        order_id = data["metadata"].get("order_id")

        order = await session.get(Order, int(order_id))

        if not order:
            return {"status": "order not found"}

        if order.status == OrderStatus.PAID:
            return {"status": "already paid"}

        order.status = OrderStatus.PAID
        order.stripe_payment_intent_id = data.get("payment_intent")
        order.paid_at = datetime.now(timezone.utc)

        cart_service = CartService(CartRepository(session))
        await cart_service.clear_cart_items(order.user_id)

        await session.commit()

        return {"status": "ok"}

    elif event_type == "checkout.session.expired":
        order_id = data["metadata"].get("order_id")

        order = await session.get(Order, int(order_id))
        if order:
            order.status = OrderStatus.EXPIRED
            await session.commit()

    return {"status": "ignored"}


async def create_checkout_session_service(user, session: AsyncSession) -> dict:
    """Create a Stripe Checkout Session for the user's current order/cart.

    Prices are always taken from the latest Product data to reflect updates.
    PENDING orders have an expires_at field; expired orders are ignored.
    """

    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(Order)
        .where(Order.user_id == user.id)
        .where(Order.status == OrderStatus.PENDING)
        .where(
            or_(
                Order.expires_at == None,
                Order.expires_at > now
            )
        )
        .options(selectinload(Order.items))
    )
    order: Order | None = result.scalar_one_or_none()

    if not order:
        order = Order(
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=Decimal("0.00"),
            expires_at=now + timedelta(minutes=10),
        )
        session.add(order)
        await session.commit()
    else:
        order.expires_at = now + timedelta(minutes=10)
        order.checkout_session_id = None
        order.items.clear()
        order.total_amount = Decimal("0.00")

    cart_service = CartService(CartRepository(session))
    cart = await cart_service.get_cart(user.id)

    if not cart.items:
        raise HTTPException(400, "Cart is empty")

    order_items = []
    total_amount = Decimal("0.00")

    for item in cart.items:
        product = await session.get(Product, item.product_id)
        if not product:
            raise HTTPException(400, f"Product {item.product_id} not found")

        price = product.price
        quantity = item.quantity

        order_items.append(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                price=price,
                quantity=quantity,
            )
        )
        total_amount += price * quantity

    order.items.extend(order_items)
    order.total_amount = total_amount

    session.add(order)
    await session.commit()

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": f"Order #{order.id} Total"},
                "unit_amount": int(order.total_amount * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{settings.REDIRECT_URL}:{settings.PORT}/webhook/success?order_id={order.id}",
        cancel_url=f"{settings.REDIRECT_URL}:{settings.PORT}/webhook/cancel?order_id={order.id}",
        customer_email=user.email,
        metadata={"order_id": str(order.id)},
    )

    order.checkout_session_id = checkout_session.id
    session.add(order)
    await session.commit()

    return {"checkout_url": checkout_session.url}
