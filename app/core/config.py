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
    redis_url: str = "redis://localhost:6379"
    DATABASE_URL: str = Field(..., description="Database URL")
    FRONTEND_URL: str = Field(..., description="Redirect to frontend")
    REDIRECT_URL: str = Field(..., description="Base redirect URL for payments")
    STRIPE_WEBHOOK_SECRET: str  #STRIPE_WEBHOOK_SECRET: str = Field(..., description="Stripe webhook")
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600
    ALGORITHM: str = "HS256"
    ALLOWED_ORIGINS: str = Field(..., description="Comma-separated list of allowed CORS origins")
    EXPIRES_AT: str = Field(..., description="Payment session Timeout")
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


    def get_frontend_url(self) -> str:
        """Get the frontend base URL (the first one in the list)"""
        return self.FRONTEND_URL


    def get_frontend_success_url(self) -> str:
        """Get URL for successful payment"""
        return f"{self.get_frontend_url()}/success"


    def get_frontend_cancel_url(self) -> str:
        """Get URL for payment cancellation"""
        return f"{self.get_frontend_url()}/cancel"


    class Config:
        """Pydantic configuration for settings management.

        Configures the settings class to read from a .env file with UTF-8 encoding.
        Environment variables take precedence over .env file values."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
