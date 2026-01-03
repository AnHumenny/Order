from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration settings.

    This class defines all configurable parameters for the FastAPI application.
    Settings are loaded from environment variables with fallback to default values.
    """

    APP_NAME: str = "Shop API"
    DEBUG: bool = False
    DATABASE_URL: str = Field(..., description="Database URL")
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    ALLOWED_ORIGINS: str = Field(..., description="Comma-separated list of allowed CORS origins")

    class Config:
        """Pydantic configuration for settings management.

                Configures the settings class to read from a .env file with UTF-8 encoding.
                Environment variables take precedence over .env file values."""
        env_file = ".env"


settings = Settings()
