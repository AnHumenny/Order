import logging
import os
from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.modules.payment.service import handle_stripe_webhook, create_checkout_session_service

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
    """Handle Stripe payment webhook events.

    Receives and verifies webhook events from Stripe payment system.
    Validates the request signature using Stripe's webhook secret,
    then processes the event asynchronously.
    """

    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    return await handle_stripe_webhook(event, session)


@router.post("/create-checkout-session")
async def create_checkout_session(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a Stripe Checkout Session for the current user.

    Generates a Stripe Checkout Session for the authenticated user's cart/order,
    allowing them to proceed to payment. Typically redirects to Stripe's hosted
    checkout page.

    Authentication is required.
    """
    return await create_checkout_session_service(user, session)


@router.get("/success")
async def payment_success(request: Request):
    """Endpoint for successful payment. Redirects to the frontend"""

    frontend_url = settings.get_frontend_success_url()
    return RedirectResponse(url=frontend_url)


@router.get("/cancel")
async def payment_cancel(request: Request):
    """Endpoint for payment cancellation. Redirects to the frontend """

    frontend_url = settings.get_frontend_cancel_url()
    return RedirectResponse(url=frontend_url)
