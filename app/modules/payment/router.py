import datetime
import logging
import os
from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderStatus, OrderItem

router = APIRouter(
    prefix="/webhook",
    tags=["Stripe"],
)

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

logger = logging.getLogger("uvicorn")


@router.post("/")
async def stripe_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info("Stripe event: %s", event_type)

    if event_type == "checkout.session.completed":
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

        if order.status != OrderStatus.PAID:
            order.status = OrderStatus.PAID
            order.paid_at = datetime.datetime.now(datetime.timezone.utc)

            cart_service = CartService(CartRepository(session))
            await cart_service.clear_cart_items(order.user_id)

            await session.commit()

            logger.info(
                "Order %s marked as PAID and cart cleared for user %s",
                order.id,
                order.user_id
            )

    return {"status": "ok"}



@router.post("/create-checkout-session")
async def create_checkout_session(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Creates a Stripe Checkout Session for the user's existing PENDING order.
    Returns 400 if there is no pending order.
    """

    result = await session.execute(                    # повыносить в сервисы
        select(Order)
        .where(Order.user_id == user.id)
        .where(Order.status == OrderStatus.PENDING)
        .options(selectinload(Order.items))
    )
    order: Order | None = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=400,
            detail="No pending order found for the user."
        )

    if not order.items:
        cart_service = CartService(CartRepository(session))
        cart = await cart_service.get_cart(user.id)

        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

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

        order.total_amount = sum(item.price * item.quantity for item in order.items)

        await session.commit()

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": f"Order #{order.id} Total"},
                "unit_amount": int(order.total_amount * 100),  # в центах
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"http://localhost:{settings.PORT}/success",
        cancel_url=f"http://localhost:{settings.PORT}/cancel",
        customer_email=user.email,
        metadata={"order_id": str(order.id)},
    )

    order.stripe_payment_intent_id = checkout_session.payment_intent
    order.checkout_session_id = checkout_session.id    # убрать
    await session.commit()

    logger.info("Checkout session created for user %s: %s", user.email, checkout_session.id)

    return {"checkout_url": checkout_session.url}
