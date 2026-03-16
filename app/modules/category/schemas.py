from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class CategoryBase(BaseModel):
    """Base category model with common attributes."""
    name: str = Field(..., max_length=100, description="Category name")
    parent_id: Optional[int] = Field(None, description="ID of parent category (null for root categories)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Electronics",
                "parent_id": None
            }
        }
    )


class CategoryCreate(CategoryBase):
    """Pydantic model for creating a new category.

    This model is used for input validation when creating a new category
    through the API. It defines the required fields and their constraints.

    Attributes:
        name: Name of the category (required, max 100 characters)
        parent_id: Optional ID of parent category for hierarchy
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Smartphones",
                "parent_id": 1
            }
        }
    )


class CategoryUpdate(BaseModel):
    """Pydantic model for updating an existing category.

    All fields are optional since updates can be partial.

    Attributes:
        name: New name for the category
        parent_id: New parent category ID (null to make root)
    """
    name: Optional[str] = Field(None, max_length=100, description="New category name")
    parent_id: Optional[int] = Field(None, description="New parent category ID (null to make root)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Electronics",
                "parent_id": 2
            }
        }
    )


class CategoryRead(BaseModel):
    """Pydantic model for reading/displaying category data.

    This model is used for API responses to ensure consistent output format
    and to control which fields are exposed. It's automatically populated
    from SQLAlchemy model instances.

    Attributes:
        id: Unique identifier of the category (auto-generated)
        name: Name of the category
        parent_id: ID of parent category (null for root)
    """
    id: int
    name: str
    parent_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Electronics",
                "parent_id": None,
                "children_count": 5,
                "products_count": 42,
            }
        }
    )


class CategoryWithChildren(CategoryRead):
    """Category model that includes its direct children.

    Used for building hierarchical responses without deep recursion.

    Attributes:
        children: List of direct subcategories
    """
    children: List["CategoryRead"] = Field(default_factory=list, description="Direct subcategories")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Electronics",
                "parent_id": None,
                "children": [
                    {
                        "id": 2,
                        "name": "Computers",
                        "parent_id": 1
                    },
                    {
                        "id": 3,
                        "name": "Smartphones",
                        "parent_id": 1
                    }
                ],
            }
        }
    )


class CategoryTree(CategoryRead):
    """Category model for full tree representation.

    Used for displaying complete category hierarchy with nested children.

    Attributes:
        children: Recursive list of child categories
    """
    children: List["CategoryTree"] = Field(default_factory=list, description="Nested subcategories")
    all_products_count: Optional[int] = Field(None, description="Total products in this category and all subcategories")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Electronics",
                "parent_id": None,
                "children": [
                    {
                        "id": 2,
                        "name": "Computers",
                        "parent_id": 1,
                        "children": [
                            {
                                "id": 4,
                                "name": "Laptops",
                                "parent_id": 2,
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "name": "Smartphones",
                        "parent_id": 1,
                        "children": []
                    }
                ],
            }
        }
    )


class CategoryPath(BaseModel):
    """Model for category path response.

    Returns the full path from root to a specific category.

    Attributes:
        categories: List of categories in the path
        path_string: String representation of the path
    """
    categories: List[CategoryRead] = Field(..., description="Categories from root to target")
    path_string: str = Field(..., description="Path as string (e.g., 'Electronics > Computers > Laptops')")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": [
                    {
                        "id": 1,
                        "name": "Electronics",
                        "parent_id": None
                    },
                    {
                        "id": 2,
                        "name": "Computers",
                        "parent_id": 1
                    },
                    {
                        "id": 4,
                        "name": "Laptops",
                        "parent_id": 2
                    }
                ],
            }
        }
    )


class CategoryMove(BaseModel):
    """Model for moving a category to a new parent.

    Used for reorganizing category hierarchy.

    Attributes:
        new_parent_id: ID of new parent category (null to make root)
    """
    new_parent_id: Optional[int] = Field(None, description="ID of new parent category (null to make root)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "new_parent_id": 3
            }
        }
    )


class SubcategoryCreate(BaseModel):
    """Schema for creating a subcategory (only name needed)."""
    name: str = Field(..., max_length=100, description="Subcategory name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Name of subcategory"
            }
        }
    )


CategoryTree.model_rebuild()
CategoryWithChildren.model_rebuild()
