from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.products.models import Product


class Category(Base):
    """Database model representing a product category with hierarchical structure.

    Categories organize products into logical groups and provide hierarchical
    organization for the product catalog. Each category can have multiple
    subcategories and contain multiple products.

    Attributes:
        id: Primary key identifier for the category
        name: Unique name of the category (max 100 characters)
        parent_id: Foreign key to parent category (null for root categories)
        parent: Parent category relationship
        children: List of subcategories
        products: List of products belonging to this category

    Relationships:
        - Self-referential one-to-many relationship for hierarchy
        - One-to-many relationship with Product model (products can be in any category,
          not only leaf categories)
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side=[id],
        back_populates="children"
    )

    children: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    products: Mapped[List["Product"]] = relationship(
        back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name} parent_id={self.parent_id}>"


    @property
    def is_root(self) -> bool:
        """Check if category is a root category (has no parent)."""
        return self.parent_id is None


    @property
    def is_leaf(self) -> bool:
        """Check if category is a leaf category (has no children)."""
        return len(self.children) == 0


    def get_full_path(self, separator: str = " > ") -> str:
        """Get full category path from root to current category.

        Example: "Electronics > Computers > Laptops"
        """
        if self.parent:
            return f"{self.parent.get_full_path(separator)}{separator}{self.name}"
        return self.name


    def get_all_products(self) -> List["Product"]:
        """Get all products from this category and all subcategories."""
        all_products = list(self.products)
        for child in self.children:
            all_products.extend(child.get_all_products())
        return all_products
