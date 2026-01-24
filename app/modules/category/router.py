from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.database import get_session
from app.core.dependencies import get_current_admin

from app.modules.category.schemas import (
    CategoryCreate,
    CategoryRead,
)
from app.modules.category.service import CategoryRepository, CategoryService

router = APIRouter(
    prefix="/categories",
)


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    """Create a new product category.

    This endpoint allows administrators to create new categories for organizing products.
    The category name must be unique across all categories in the system.

    Args:
        data: CategoryCreate model containing the name of the new category
        session: Database session dependency
        admin: Current authenticated admin user (dependency injection)

    Returns:
        CategoryRead: The created category with its ID and name
    """

    service = CategoryService(CategoryRepository(session))
    category = await service.create_category(data.name)
    await session.commit()
    return category


@router.get(
    "/",
    response_model=list[CategoryRead],
    summary="Get all categories",
)
async def list_categories(
    session: AsyncSession = Depends(get_session),
):
    """Retrieve all product categories.

    Returns a list of all categories in the system, ordered alphabetically by name.
    This endpoint is publicly accessible and doesn't require authentication.

    Args:
        session: Database session dependency

    Returns:
        list[CategoryRead]: List of all categories
    """

    service = CategoryService(CategoryRepository(session))
    return await service.list_categories()


@router.delete(
    "/{category_id}",
    summary="Delete category",
)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    """Delete a category by its ID.

    This endpoint allows administrators to remove a category from the system.
    Note: Deleting a category may affect associated products. Consider
    product-category relationships before deletion.

    Args:
        category_id: ID of the category to delete (path parameter)
        session: Database session dependency
        admin: Current authenticated admin user (dependency injection)

    Returns:
        dict: Status message indicating successful deletion
    """

    service = CategoryService(CategoryRepository(session))
    await service.delete_category(category_id)
    await session.commit()
    return {"status": "deleted"}
