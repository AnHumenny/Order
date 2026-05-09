from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
from app.core.config import settings
from app.core.dependencies import get_current_user, get_session
from app.core.rate_limiter import limiter, RateLimits
from app.modules.currency import get_user_currency
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
@limiter.limit(RateLimits.READ)
async def create_checkout_session(
        request: Request,
        session: AsyncSession = Depends(get_session),
        user=Depends(get_current_user),
        user_currency: str = Depends(get_user_currency)
):
    """Create Stripe checkout session for current order."""

    result = await create_checkout_session_service(
        user=user,
        session=session,
        user_currency=user_currency
    )

    return result


@router.get("/cancel")
@limiter.limit(RateLimits.READ)
async def payment_cancel(request: Request):
    """Redirect user to cart page after cancelling Stripe Checkout payment."""
    return await process_payment_cancel()


@router.post("/")
@limiter.limit(RateLimits.READ)
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
@limiter.limit(RateLimits.READ)
async def order_status(request: Request, order_id: int, session: AsyncSession = Depends(get_session)):
    """Get the current status of an order.

    Used by frontend to poll for payment confirmation after Stripe redirect.
    Returns "success", "pending", or "error" with a descriptive message.
    """
    return await get_order_status(order_id, session)
