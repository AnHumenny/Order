from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.users.router import router as users_router
from app.modules.products.router import router as products_router
from app.modules.cart.router import router as cart_router
from app.modules.orders.router import router as orders_router


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

# --- Подключаем роутеры ---
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
