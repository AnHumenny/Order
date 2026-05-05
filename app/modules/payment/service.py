import stripe
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from starlette.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.modules.cart.service import CartService
from app.modules.cart.repository import CartRepository
from app.modules.orders.models import Order, OrderStatus


async def create_checkout_session_service(user, session: AsyncSession) -> dict:
    """Creates a Stripe Checkout Session for the current PENDING order."""

    result = await session.execute(
        select(Order)
        .where(
            Order.user_id == user.id,
            Order.status == OrderStatus.PENDING
        )
        .order_by(Order.created_at.desc())
        .limit(1)
        .options(selectinload(Order.items))
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(400, "No active order found. Please checkout first.")

    if order.expires_at and order.expires_at < datetime.now(timezone.utc):
        order.status = OrderStatus.EXPIRED
        await session.commit()
        raise HTTPException(400, "Order expired. Please checkout again.")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",  # если потом добавишь мультивалютность – заменишь
                    "product_data": {
                        "name": f"Order #{order.id}",
                    },
                    "unit_amount": int(order.total_amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.get_frontend_success_url()}?order_id={order.id}",
            cancel_url=settings.get_frontend_cancel_url(),
            customer_email=user.email,
            metadata={
                "order_id": str(order.id),
                "user_id": str(user.id)
            },
        )

    except stripe.error.AuthenticationError:
        raise HTTPException(500, "Stripe authentication failed. Please check API key.")
    except stripe.error.InvalidRequestError as e:
        raise HTTPException(400, f"Invalid payment request: {e}")
    except stripe.error.RateLimitError:
        raise HTTPException(429, "Too many requests. Try later.")
    except stripe.error.StripeError as e:
        raise HTTPException(500, f"Stripe error: {e}")
    except Exception as e:
        raise HTTPException(500, "Unexpected error creating payment session.")

    order.checkout_session_id = checkout_session.id
    await session.commit()


    return {
        "checkout_url": checkout_session.url,
        "order_id": order.id
    }


async def process_payment_cancel():
    """Process payment cancellation.

    Returns a redirect response to the frontend cart page when a user
    cancels the payment flow in Stripe Checkout.

    Returns:
        RedirectResponse: Redirect to frontend cart URL
    """

    frontend_cart_url = settings.get_frontend_cancel_url()
    return RedirectResponse(url=frontend_cart_url)


async def handle_stripe_webhook(event: dict, session: AsyncSession):
    """Processes the Stripe webhook, updates the status of an existing order, and clears the shopping cart."""

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type != "checkout.session.completed":
        return {"status": "ignored"}

    metadata = data.get("metadata") or {}
    order_id = int(metadata.get("order_id", 0))

    if not order_id:
        return {"status": "ignored", "error": "no order_id in metadata"}

    order = await session.get(Order, order_id)

    if not order:
        return {"status": "error", "error": f"Order {order_id} not found"}

    if order.status == OrderStatus.PAID:
        return {"status": "already paid"}

    order.status = OrderStatus.PAID
    order.paid_at = datetime.now(timezone.utc)
    order.stripe_payment_intent_id = data.get("payment_intent")

    await session.commit()

    cart_service = CartService(CartRepository(session))
    await cart_service.clear_cart_items(order.user_id)

    return {"status": "success", "order_id": order.id}


async def get_order_status(order_id: int, session: AsyncSession):
    """API for checking the order status (front)"""

    order = await session.get(Order, order_id)
    if not order:
        return {"status": "error", "message": "Заказ не найден"}
    if order.status == OrderStatus.PAID:
        return {"status": "success", "message": "Оплата прошла успешно"}
    elif order.status == OrderStatus.PENDING:
        return {"status": "pending", "message": "Оплата в обработке"}
    else:
        return {"status": "error", "message": "Платёж не прошёл или заказ истёк"}
