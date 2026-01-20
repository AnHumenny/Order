from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.products.models import Product


class Category(Base):
    """Database model representing a product category.

    Categories organize products into logical groups and provide hierarchical
    organization for the product catalog. Each category can contain multiple
    products.

    Attributes:
        id: Primary key identifier for the category
        name: Unique name of the category (max 100 characters)
        products: List of products belonging to this category

    Relationships:
        - One-to-many relationship with Product model
        - Each category can have multiple products
        - Each product belongs to one category
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name}>"
