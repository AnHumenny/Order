import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(
        amount: int,
        user_currency: str = "usd",
        original_amount_usd: float = None,
        metadata: dict = None
) -> stripe.PaymentIntent:
    """Create a Stripe Payment Intent with proper currency handling."""

    if user_currency.upper() in ["BYN", "UAH", "KZT"]:
        payment_currency = "usd"
        payment_amount = int(original_amount_usd * 100) if original_amount_usd else amount
    else:
        payment_currency = user_currency.lower()
        payment_amount = amount

    metadata = metadata or {}
    metadata["original_currency"] = user_currency
    metadata["original_amount"] = str(amount)
    metadata["payment_currency"] = payment_currency

    return stripe.PaymentIntent.create(
        amount=payment_amount,
        currency=payment_currency,
        metadata=metadata,
        description=f"Payment in {user_currency} (processed as {payment_currency})",
        automatic_payment_methods={"enabled": True},
    )
