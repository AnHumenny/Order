from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
from app.core.config import settings
from app.core.database import get_session
from app.modules.orders.models import OrderStatus
from app.modules.orders.repository import get_order_by_id

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_session)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        raise HTTPException(400)

    intent = event["data"]["object"]
    order_id = intent["metadata"].get("order_id")

    order = get_order_by_id(db, int(order_id))
    if not order:
        return {"ok": False}

    if event["type"] == "payment_intent.succeeded":
        order.status = OrderStatus.PAID

    elif event["type"] == "payment_intent.payment_failed":
        order.status = OrderStatus.FAILED

    db.commit()
    return {"ok": True}
