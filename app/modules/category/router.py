from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing import Optional

from app.core.database import get_session
from app.core.dependencies import get_current_admin

from app.modules.category.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryTree, SubcategoryCreate,
)
from app.modules.category.service import CategoryService
from app.modules.category.repository import CategoryRepository

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
    category = await service.create_category(data)
    await session.commit()
    return category


@router.post(
    "/{parent_id}/subcategories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create subcategory",
)
async def create_subcategory(
        parent_id: int,
        data: SubcategoryCreate,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """Create a new subcategory under a parent category."""
    category_data = CategoryCreate(
        name=data.name,
        parent_id=parent_id
    )

    service = CategoryService(CategoryRepository(session))
    category = await service.create_category(category_data)
    await session.commit()
    return category


@router.get(
    "/",
    response_model=list[CategoryRead],
    summary="Get all categories",
)
async def list_categories(
        session: AsyncSession = Depends(get_session),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hierarchy: bool = Query(False, description="Include parent/children info"),
):
    """Retrieve all product categories.

    Returns a list of all categories in the system, ordered alphabetically by name.
    This endpoint is publicly accessible and doesn't require authentication.

    Args:
        session: Database session dependency
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_hierarchy: Whether to include parent/children information

    Returns:
        list[CategoryRead]: List of all categories
    """

    service = CategoryService(CategoryRepository(session))
    return await service.list_categories(skip, limit, include_hierarchy)


@router.get(
    "/root",
    response_model=list[CategoryRead],
    summary="Get root categories",
)
async def get_root_categories(
        session: AsyncSession = Depends(get_session),
):
    """Get all root categories (categories without a parent).

    Returns:
        list[CategoryRead]: List of root categories
    """
    service = CategoryService(CategoryRepository(session))
    return await service.get_root_categories()


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Get category by ID",
)
async def get_category(
        category_id: int,
        session: AsyncSession = Depends(get_session),
        include_children: bool = Query(False, description="Include subcategories"),
):
    """Get a specific category by its ID.

    Args:
        category_id: ID of the category
        session: Database session dependency
        include_children: Whether to include subcategories in the response

    Returns:
        CategoryRead: Category details
    """
    service = CategoryService(CategoryRepository(session))
    category = await service.get_category_by_id(category_id, include_children)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get(
    "/{category_id}/children",
    response_model=list[CategoryRead],
    summary="Get direct subcategories",
)
async def get_subcategories(
        category_id: int,
        session: AsyncSession = Depends(get_session),
):
    """Get direct subcategories of a category.

    Args:
        category_id: ID of the parent category
        session: Database session dependency

    Returns:
        list[CategoryRead]: List of direct subcategories
    """
    service = CategoryService(CategoryRepository(session))
    return await service.get_subcategories(category_id)


@router.get(
    "/{category_id}/tree",
    response_model=CategoryTree,
    summary="Get category tree",
)
async def get_category_tree(
        category_id: int,
        session: AsyncSession = Depends(get_session),
        depth: Optional[int] = Query(None, ge=1, description="Maximum depth of the tree"),
):
    """Get full category tree with all descendants.

    Args:
        category_id: ID of the root category
        session: Database session dependency
        depth: Maximum depth of the tree (optional)

    Returns:
        CategoryTree: Category tree structure
    """
    service = CategoryService(CategoryRepository(session))
    tree = await service.get_category_tree(category_id, depth)
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return tree


@router.get(
    "/{category_id}/path",
    response_model=list[CategoryRead],
    summary="Get category path",
)
async def get_category_path(
        category_id: int,
        session: AsyncSession = Depends(get_session),
):
    """Get full path from root to the specified category.

    Args:
        category_id: ID of the category
        session: Database session dependency

    Returns:
        list[CategoryRead]: List of categories from root to the specified category
    """
    service = CategoryService(CategoryRepository(session))
    path = await service.get_category_path(category_id)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return path


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Update category",
)
async def update_category(
        category_id: int,
        data: CategoryUpdate,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """Update a category.

    Args:
        category_id: ID of the category to update
        data: Update data (name, parent_id)
        session: Database session dependency
        admin: Current authenticated admin user

    Returns:
        CategoryRead: Updated category
    """
    service = CategoryService(CategoryRepository(session))
    category = await service.update_category(category_id, data)
    await session.commit()
    return category


@router.delete(
    "/{category_id}",
    summary="Delete category",
)
async def delete_category(
        category_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
        force: bool = Query(False, description="Force delete even if has children"),
):
    """Delete a category by its ID.

    This endpoint allows administrators to remove a category from the system.
    By default, categories with subcategories cannot be deleted unless force=True.

    Args:
        category_id: ID of the category to delete
        session: Database session dependency
        admin: Current authenticated admin user
        force: If True, delete category and all its subcategories

    Returns:
        dict: Status message indicating successful deletion
    """

    service = CategoryService(CategoryRepository(session))
    await service.delete_category(category_id, force)
    await session.commit()
    return {"status": "deleted"}


@router.delete(
    "/{category_id}/subcategories/{subcategory_id}",
    summary="Delete subcategory",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_subcategory(
        category_id: int,
        subcategory_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """Delete a specific subcategory.

    This endpoint allows administrators to delete a subcategory.
    Verifies that the subcategory actually belongs to the specified parent.

    Args:
        category_id: ID of the parent category
        subcategory_id: ID of the subcategory to delete
        session: Database session dependency
        admin: Current authenticated admin user

    Returns:
        None (204 No Content)
    """
    service = CategoryService(CategoryRepository(session))

    subcategory = await service.get_category_by_id(subcategory_id)
    if not subcategory or subcategory.parent_id != category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcategory with id {subcategory_id} not found under category {category_id}"
        )

    await service.delete_category(subcategory_id, force=False)
    await session.commit()


@router.post(
    "/{category_id}/move",
    response_model=CategoryRead,
    summary="Move category to new parent",
)
async def move_category(
        category_id: int,
        new_parent_id: Optional[int] = Query(None, description="ID of new parent (null for root)"),
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """Move a category to a new parent.

    Args:
        category_id: ID of the category to move
        new_parent_id: ID of new parent category (null to make root)
        session: Database session dependency
        admin: Current authenticated admin user

    Returns:
        CategoryRead: Updated category
    """
    service = CategoryService(CategoryRepository(session))
    category = await service.move_category(category_id, new_parent_id)
    await session.commit()
    return category


@router.get(
    "/{category_id}/products/count",
    summary="Get products count in category",
)
async def get_category_products_count(
        category_id: int,
        session: AsyncSession = Depends(get_session),
        include_subcategories: bool = Query(False, description="Include products from subcategories"),
):
    """Get count of products in a category.

    Args:
        category_id: ID of the category
        session: Database session dependency
        include_subcategories: Whether to include products from subcategories

    Returns:
        dict: Category ID and products count
    """
    service = CategoryService(CategoryRepository(session))
    count = await service.get_products_count(category_id, include_subcategories)
    return {
        "category_id": category_id,
        "products_count": count,
        "include_subcategories": include_subcategories
    }
