from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings.

    This class defines all configurable parameters for the FastAPI application.
    Settings are loaded from environment variables with fallback to default values.
    """

    APP_NAME: str = "Shop API"
    DEBUG: bool = False
    DATABASE_URL: str = Field(..., description="Database URL")
    frontend_url: str = "http://localhost:5173"
    BASIC_URL: str = Field(default="http://localhost:5173", description="Basic URL for frontend")   # костыль
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    ALLOWED_ORIGINS: str = Field(..., description="Comma-separated list of allowed CORS origins")
    PORT: int
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(
        None,
        description="Stripe publishable key for client-side payments"
    )
    STRIPE_SECRET_KEY: Optional[str] = Field(
        None,
        description="Stripe secret key for server-side operations"
    )
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(
        None,
        description="Secret for verifying Stripe webhook signatures"
    )
    STRIPE_ENDPOINT_SECRET: Optional[str] = Field(
        None,
        description="Endpoint secret for Stripe webhooks (alias for webhook secret)"
    )

    class Config:
        """Pydantic configuration for settings management.

        Configures the settings class to read from a .env file with UTF-8 encoding.
        Environment variables take precedence over .env file values."""
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
