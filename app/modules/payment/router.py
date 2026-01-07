from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderStatus
from app.users.models import User

router = APIRouter(
    prefix="/webhook",
    tags=["Stripe Webhook"],
)

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/")
async def stripe_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400)

    if event["type"] == "checkout.session.completed":
        checkout = event["data"]["object"]

        checkout_session_id = checkout["id"]

        order = await session.scalar(
            select(Order)
            .where(Order.checkout_session_id == checkout_session_id)
        )

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == OrderStatus.PAID:
            return {"status": "already processed"}

        order.status = OrderStatus.PAID
        order.paid_at = datetime.utcnow()

        new_order = Order(
            user_id=order.user_id,
            status=OrderStatus.DRAFT,
        )

        session.add(new_order)
        await session.commit()

        print(f"Order {order.id} marked as PAID")

    return {"status": "ok"}


@router.post("/create-checkout-session")
async def create_checkout_session(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Creates a Stripe Checkout Session for the amount of the user's shopping cart"""

    cart_service = CartService(CartRepository(session))
    cart = await cart_service.get_cart(user.id)

    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = sum(item.price * item.quantity for item in cart.items)
    unit_amount = int(total_amount * 100)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "Your Cart Total"},
                "unit_amount": unit_amount,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
        customer_email=user.email,
    )

    return {"checkout_url": checkout_session.url}