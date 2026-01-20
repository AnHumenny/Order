from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Pydantic model for creating a new category.

    This model is used for input validation when creating a new category
    through the API. It defines the required fields and their constraints.

    Attributes:
        name: Name of the category (required, max 100 characters)
    """
    name: str = Field(..., max_length=100, example="Electronics")


class CategoryRead(BaseModel):
    """Pydantic model for reading/displaying category data.

    This model is used for API responses to ensure consistent output format
    and to control which fields are exposed. It's automatically populated
    from SQLAlchemy model instances.

    Attributes:
        id: Unique identifier of the category (auto-generated)
        name: Name of the category
    """

    id: int
    name: str

    class Config:
        from_attributes = True
