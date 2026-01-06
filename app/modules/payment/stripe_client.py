import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount: int, metadata: dict) -> stripe.PaymentIntent:
    return stripe.PaymentIntent.create(
        amount=amount,
        currency="eur",
        metadata=metadata,
        automatic_payment_methods={"enabled": True},
    )
