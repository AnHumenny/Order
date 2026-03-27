from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.core.config import settings
from app.users.router import router as users_router
from app.modules.category.router import router as categories_router
from app.modules.products.router import router as products_router
from app.modules.products.gallery.routes import router as product_images_router
from app.modules.cart.router import router as cart_router
from app.modules.orders.router import router as orders_router
from app.modules.payment.router import router as payment_router
from app.modules.analytics.router import router as analytics_router
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
frontend_url = os.getenv("FRONTEND_URL")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,              # type: ignore
    allow_origins=os.getenv("ALLOWED_ORIGINS"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(users_router, tags=["Users"])
app.include_router(categories_router, tags=["Category"])
app.include_router(products_router, tags=["Products"])
app.include_router(product_images_router,  tags=["Product Images"])
app.include_router(cart_router, tags=["Cart"])
app.include_router(orders_router, tags=["Orders"])
app.include_router(analytics_router, tags=["Analytics"])
app.include_router(payment_router, tags=["Stripe"])
