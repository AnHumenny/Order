import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
env_file = os.getenv("ENV_ORDER_FILE", ".env")

if Path(env_file).exists():
    load_dotenv(env_file)

class Settings(BaseSettings):
    """Application configuration settings."""

    APP_NAME: str = "Shop API"
    DEBUG: bool = False
    ENABLE_API_DOCS: bool = False

    DATABASE_URL: str = Field(..., description="Database URL")

    FRONTEND_URL: str = Field(..., description="Frontend URL")
    REDIRECT_URL: str = Field(..., description="Base redirect URL for payments")
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )

    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600

    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis URL for caching (optional)"
    )
    CACHE_PREFIX: str = "fastapi-cache"
    CACHE_DEFAULT_EXPIRE: int = 60
    CACHE_EXPIRE_MENU: int = 60
    CACHE_EXPIRE_SUBMENU: int = 60
    CACHE_EXPIRE_CATEGORY_TREE: int = 300

    CACHE_NAMESPACE_MENU: str = "menu"
    CACHE_NAMESPACE_SUBMENU: str = "sub_menu"
    CACHE_NAMESPACE_CATEGORY_TREE: str = "category_tree"

    IMAGE_MAX_WIDTH: int = 1920
    IMAGE_MAX_HEIGHT: int = 1920
    IMAGE_WEBP_QUALITY: int = 85
    IMAGE_THUMBNAIL_SIZE: int = 200
    MAX_IMAGE_SIZE_MB: int = 5

    PORT: int = Field(default=8000, description="Server port")

    YOOKASSA_SHOP_ID: Optional[str] = Field(
        None, description="YooKassa shop ID"
    )
    YOOKASSA_SECRET_KEY: Optional[str] = Field(
        None, description="YooKassa secret key"
    )

    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(
        None, description="Stripe publishable key"
    )
    STRIPE_SECRET_KEY: Optional[str] = Field(
        None, description="Stripe secret key"
    )
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(
        None, description="Secret for verifying Stripe webhook signatures"
    )

    STRIPE_SUPPORTED_CURRENCIES: str = Field(
        default="usd,eur,gbp,jpy,cad,aud,chf,cny,pln,rub",
        description="Comma-separated list of currencies supported by Stripe"
    )

    EXPIRES_AT: int = Field(
        default=3600,
        description="Payment session timeout in seconds"
    )

    RATE_LIMIT_ENABLED: bool = Field(default=True)
    DEFAULT_RATE_LIMIT: str = Field(default="1000/hour")                # подрезаем для теста
    RATE_LIMIT_AUTH: str = Field(default="3/minute")
    RATE_LIMIT_WRITE: str = Field(default="15/minute")
    RATE_LIMIT_READ: str = Field(default="20/minute")

    TRUSTED_IPS: str = Field(
        default="127.0.0.1,172.17.0.1,10.0.0.0/8",
        description="Comma-separated trusted IPs (no rate limit)"
    )

    path_to_image: str = "static/products/"

    @property
    def trusted_ips_list(self) -> List[str]:
        return [ip.strip() for ip in self.TRUSTED_IPS.split(",") if ip.strip()]

    @property
    def REDIS_RATE_LIMIT_URL(self) -> Optional[str]:
        """Get Redis URL for rate limiter (use separate DB by default)."""

        if not self.REDIS_URL:
            return None

        if self.REDIS_URL.endswith('/'):
            return f"{self.REDIS_URL}1"

        if '/0' in self.REDIS_URL or '/1' in self.REDIS_URL or '/2' in self.REDIS_URL:
            return self.REDIS_URL

        return f"{self.REDIS_URL}/1"

    @property
    def stripe_supported_currencies(self) -> List[str]:
        """Get list of currencies supported by Stripe."""

        currencies = os.getenv("STRIPE_SUPPORTED_CURRENCIES", "usd,eur,gbp,jpy,cad,aud,chf,cny,pln,rub")
        return [c.strip().lower() for c in currencies.split(",")]

    @property
    def stripe_fallback_currency(self) -> str:
        """Currency to use when user's currency is not supported by Stripe."""
        return os.getenv("STRIPE_FALLBACK_CURRENCY", "usd")

    def get_frontend_url(self) -> str:
        return self.FRONTEND_URL

    def get_frontend_success_url(self) -> str:
        return f"{self.get_frontend_url()}/success"

    def get_frontend_cancel_url(self) -> str:
        return f"{self.get_frontend_url()}/cancel"

    class Config:
        env_file = env_file
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()   # type: ignore[call-arg]
