import os
import stripe
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from starlette.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from redis import asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.rate_limiter import setup_rate_limiter

from app.modules.private_modules.admin import admin
from app.modules.private_modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.category.router import router as categories_router
from app.modules.products.router import router as products_router
from app.modules.products.gallery.routes import router as product_images_router
from app.modules.cart.router import router as cart_router
from app.modules.orders.router import router as orders_router
from app.modules.private_modules.payment.stripe.stripe_router import router as payment_router
from app.modules.analytics.router import router as analytics_router
from app.modules.private_modules.currency.router import router as currencies_router
from app.modules.private_modules.payment.yookassa.yookassa_router import router as yookassa_router

setup_logging()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

FRONTEND_URL = os.getenv("FRONTEND_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    FastAPICache.init(
        RedisBackend(redis_client),
        prefix=settings.CACHE_PREFIX,
        expire=settings.CACHE_DEFAULT_EXPIRE,
    )
    yield
    await redis_client.close()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds basic security headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
    redirect_slashes=False,
    docs_url="/swagger" if settings.ENABLE_API_DOCS else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.ENABLE_API_DOCS else None,
)


allowed_origins = list(settings.ALLOWED_ORIGINS)

if FRONTEND_URL:
    frontend = FRONTEND_URL.rstrip("/")
    if frontend not in allowed_origins:
        allowed_origins.append(frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="admin_session",
    max_age=3600 * 24,
    same_site="strict",
    https_only=True,
)

setup_rate_limiter(app)

app.add_middleware(SecurityHeadersMiddleware)


admin.mount_to(app)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router, tags=["Auth"])
app.include_router(users_router, tags=["Users"])
app.include_router(products_router, tags=["Products"])
app.include_router(categories_router, tags=["Category"])
app.include_router(product_images_router, tags=["Product Images"])
app.include_router(cart_router, tags=["Cart"])
app.include_router(orders_router, tags=["Orders"])
app.include_router(analytics_router, tags=["Analytics"])
app.include_router(currencies_router, tags=["Currencies"])
app.include_router(yookassa_router, tags=["YooKassa"])
app.include_router(payment_router, tags=["Stripe"])


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title=settings.APP_NAME,
    )
