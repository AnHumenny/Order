from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    """User model representing application users.

    Stores user authentication details, permissions, and timestamps.
    Users can have carts and place orders.

    Attributes:
        id: Unique user identifier
        email: User's email address (used for authentication)
        hashed_password: Securely hashed password
        is_active: Whether user account is active/enabled
        is_superuser: Whether user has admin privileges
        updated_at: Timestamp of last update
        created_at: Timestamp of account creation
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f"<User id={self.id} email={self.email}>"
