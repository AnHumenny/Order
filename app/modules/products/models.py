from decimal import Decimal
from typing import Optional, TYPE_CHECKING, List, Dict, Any
from sqlalchemy import String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.category.models import Category
    from app.modules.products.gallery.models import ProductImage


class Product(Base):
    """Product model with category relationship and image handling."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.order",
        lazy="selectin"
    )

    @property
    def main_image(self) -> Optional["ProductImage"]:
        return next((img for img in self.images if img.is_main), self.images[0] if self.images else None)

    @property
    def gallery_images(self) -> List["ProductImage"]:
        return [img for img in self.images if not img.is_main]

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}>"
