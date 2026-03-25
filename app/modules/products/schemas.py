from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from app.modules.category.schemas import CategoryRead, CategoryTree
from app.modules.products.gallery.schemas import ProductImageRead


class ProductBase(BaseModel):
    """Base product schema with common attributes."""

    name: str = Field(..., max_length=255, description="Product name", json_schema_extra={"example": "iPhone 13"})
    description: Optional[str] = Field(None, max_length=1000, description="Product description",
                                       json_schema_extra={"example": "The latest iPhone model"})
    price: Decimal = Field(..., gt=0, description="Product price", json_schema_extra={"example": 999.99})
    category_id: int = Field(..., gt=0, description="Category ID", json_schema_extra={"example": 1})


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "iPhone 13",
                "description": "The latest iPhone model",
                "price": 999.99,
                "category_id": 1
            }
        }
    )


class ProductUpdate(BaseModel):
    """Schema for updating existing products."""

    name: Optional[str] = Field(None, max_length=255, description="New product name")
    description: Optional[str] = Field(None, max_length=1000, description="New description")
    price: Optional[Decimal] = Field(None, gt=0, description="New price")
    category_id: Optional[int] = Field(None, gt=0, description="New category ID")
    is_active: Optional[bool] = Field(None, description="New active status")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "iPhone 14",
                "price": 1099.99,
                "category_id": 2
            }
        }
    )


class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[Dict[str, Any]] = None
    price: Decimal
    is_active: bool
    category_id: Optional[int] = None
    category: Optional["CategoryRead"] = None
    images: List["ProductImageRead"] = []

    model_config = ConfigDict(from_attributes=True)


class ProductDetailRead(ProductRead):
    """Detailed product schema with separated main and gallery images."""

    main_image: Optional[ProductImageRead] = Field(
        None,
        description="Main product image"
    )
    gallery_images: List[ProductImageRead] = Field(
        default_factory=list,
        description="Additional gallery images (excluding main)"
    )

    @classmethod
    def from_product(cls, product):
        """Create detailed schema from product model."""
        data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "is_active": product.is_active,
            "category_id": product.category_id,
            "category": product.category,
            "images": product.images,
            "main_image": product.main_image,
            "gallery_images": product.gallery_images,
        }
        return cls(**data)


class ProductWithFullCategory(ProductRead):
    """Extended product schema with complete category tree."""

    category_tree: Optional[CategoryTree] = Field(
        None,
        description="Full category tree from root to product's category"
    )


class ProductFilterParams(BaseModel):
    """Product filtering and pagination parameters."""

    search: Optional[str] = Field(None, description="Search in name and description")
    min_price: Optional[float] = Field(None, gt=0, description="Minimum price")
    max_price: Optional[float] = Field(None, gt=0, description="Maximum price")
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="Filter by category ID"
    )
    include_subcategories: bool = Field(
        False,
        description="Include products from all subcategories"
    )
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")
    is_active: Optional[bool] = Field(
        True,
        description="Filter by active status"
    )
    has_images: Optional[bool] = Field(
        None,
        description="Filter products with/without images"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "search": "iphone",
                "min_price": 500,
                "max_price": 1500,
                "category_id": 2,
                "include_subcategories": True,
                "skip": 0,
                "limit": 20,
                "has_images": True
            }
        }
    )


class ProductFilter(BaseModel):
    """Product filter schema for list responses (lightweight version)."""

    id: int
    name: str
    description: Optional[Dict[str, Any]] = None
    price: float
    category_id: Optional[int] = None
    category_name: Optional[str] = Field(
        None,
        description="Category name for quick reference"
    )
    is_active: bool
    has_images: bool = Field(
        False,
        description="Whether product has any images"
    )
    main_image_url: Optional[str] = Field(
        None,
        description="URL of main product image (if exists)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "iPhone 13",
                "price": 999.99,
                "category_name": "Smartphones",
                "is_active": True,
                "has_images": True,
                "main_image_url": "/static/products/main/1_abc123.jpg"
            }
        }
    )


class ProductsByCategoryResponse(BaseModel):
    """Response schema for products grouped by category."""

    category_id: int
    category_name: str
    category_path: str
    products: List[ProductRead]
    total_count: int
    include_subcategories: bool
    subcategories_used: Optional[List[int]] = Field(
        None,
        description="List of subcategory IDs that were included"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": 2,
                "category_name": "Smartphones",
                "category_path": "Electronics > Smartphones",
                "total_count": 15,
                "include_subcategories": True,
                "subcategories_used": [2, 5, 6]
            }
        }
    )


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: List[ProductRead]
    total: int
    skip: int
    limit: int
    has_more: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "skip": 0,
                "limit": 20,
                "has_more": True
            }
        }
    )


class ProductDelete(BaseModel):
    """Response schema for product deletion."""

    id: int
    status: str = "deleted"
    message: str = "Product successfully deleted"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "status": "deleted",
                "message": "Product successfully deleted"
            }
        }
    )


class ProductDescription(BaseModel):
    main: str = ""
    specs: str = ""
    features: str = ""
    reviews: str = ""

    model_config = ConfigDict(from_attributes=True)
