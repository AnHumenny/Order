import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount: int, metadata: dict) -> stripe.PaymentIntent:
    """Create a Stripe Payment Intent for processing payments.

    Initializes a Payment Intent with the specified amount and metadata.
    Automatically enables various payment methods as configured by Stripe.
    """

    return stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        metadata=metadata,
        automatic_payment_methods={"enabled": True},
    )
