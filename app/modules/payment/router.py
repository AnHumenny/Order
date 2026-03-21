from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
from app.core.config import settings
from app.core.dependencies import get_current_user, get_session
from app.modules.payment.service import (
    create_checkout_session_service,
    process_payment_cancel,
    handle_stripe_webhook,
    get_order_status
)

router = APIRouter(
    prefix="/webhook",
    tags=["Stripe"],
)

@router.post("/create-checkout-session")
async def create_checkout_session(user=Depends(get_current_user),
                                  session: AsyncSession = Depends(get_session)):
    """Create a Stripe Checkout Session for the current user.

        Generates a Stripe Checkout Session for the authenticated user's cart/order,
        allowing them to proceed to payment. Typically redirects to Stripe's hosted
        checkout page.

        Authentication is required.
        """
    return await create_checkout_session_service(user, session)


@router.get("/cancel")
async def payment_cancel():
    return await process_payment_cancel()


@router.post("/")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """Handle Stripe payment webhook events.

        Receives and verifies webhook events from Stripe payment system.
        Validates the request signature using Stripe's webhook secret,
        then processes the event asynchronously.
        """

    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return {"status": "invalid signature"}

    return await handle_stripe_webhook(event, session)


@router.get("/status")
async def order_status(order_id: int, session: AsyncSession = Depends(get_session)):
    return await get_order_status(order_id, session)
