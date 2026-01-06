from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.users.router import router as users_router
from app.modules.products.router import router as products_router
from app.modules.cart.router import router as cart_router
from app.modules.orders.router import router as orders_router
from app.modules.payment.router import router as payment_router
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

origins = settings.ALLOWED_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,              # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, tags=["Users"])
app.include_router(products_router, tags=["Products"])
app.include_router(cart_router, tags=["Cart"])
app.include_router(orders_router, tags=["Orders"])
app.include_router(payment_router, tags=["Payment"])
