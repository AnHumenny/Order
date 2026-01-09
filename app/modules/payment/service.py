import datetime
import logging
from decimal import Decimal
import stripe
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderStatus, OrderItem

logger = logging.getLogger(__name__)


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
            - {"status": "ok"}: If order successfully updated to PAID

    Raises:
        SQLAlchemyError: If database operation fail
    """

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info("Stripe event: %s", event_type)

    if event_type != "checkout.session.completed":
        return {"status": "ignored"}

    payment_intent_id = data.get("payment_intent")
    checkout_session_id = data.get("id")

    order = await session.scalar(
        select(Order).where(
            (Order.checkout_session_id == checkout_session_id) |
            (Order.stripe_payment_intent_id == payment_intent_id)
        )
    )

    if not order:
        logger.error(
            "Order not found for session %s / PI %s",
            checkout_session_id,
            payment_intent_id
        )
        return {"status": "order not found"}

    if order.status == OrderStatus.PAID:
        return {"status": "already paid"}

    order.stripe_payment_intent_id = payment_intent_id
    order.status = OrderStatus.PAID
    order.paid_at = datetime.datetime.now(datetime.timezone.utc)

    cart_service = CartService(CartRepository(session))
    await cart_service.clear_cart_items(order.user_id)

    session.add(order)
    await session.commit()

    logger.info(
        "Order %s marked as PAID, PI set, and cart cleared for user %s",
        order.id,
        order.user_id
    )

    return {"status": "ok"}


async def create_checkout_session_service(user, session: AsyncSession) -> dict:
    """Create a Stripe Checkout Session for user's pending order.

    Retrieves or creates a pending order for the user, converts cart items
    to order items if needed, and creates a Stripe Checkout Session for payment.

    Args:
        user: Authenticated user object
        session: Async database session

    Returns:
        dict: Contains Stripe Checkout Session URL:
            - checkout_url: URL to redirect user for payment

    Raises:
        HTTPException 400: If no pending order exists
        HTTPException 400: If cart is empty when creating order items
        HTTPException 500: If Stripe API or database operation fails
    """

    result = await session.execute(
        select(Order)
        .where(Order.user_id == user.id)
        .where(Order.status == OrderStatus.PENDING)
        .options(selectinload(Order.items))
    )
    order: Order | None = result.scalar_one_or_none()

    if not order:
        raise HTTPException(400, "No pending order found for the user.")

    if not order.items:
        cart_service = CartService(CartRepository(session))
        cart = await cart_service.get_cart(user.id)

        if not cart.items:
            raise HTTPException(400, "Cart is empty")

        order_items = [
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
            )
            for item in cart.items
        ]

        order.items.extend(order_items)
        order.total_amount = sum(
            (item.price * item.quantity for item in cart.items), Decimal("0.00")
        )

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
        success_url=f"http://localhost:{settings.PORT}/success",
        cancel_url=f"http://localhost:{settings.PORT}/cancel",
        customer_email=user.email,
        metadata={"order_id": str(order.id)},
    )

    order.checkout_session_id = checkout_session.id

    session.add(order)
    await session.commit()

    logger.info(
        "Checkout session created for user %s: %s",
        user.email,
        checkout_session.id
    )

    return {"checkout_url": checkout_session.url}
