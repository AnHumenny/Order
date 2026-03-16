from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.core.database import get_session
from app.core.dependencies import get_current_admin
from app.modules.products.repository import ProductRepository
from app.modules.category.repository import CategoryRepository
from app.modules.products.schemas import (
    ProductRead,
    ProductCreate,
    ProductUpdate,
    ProductFilterParams,
    ProductFilter,
)
from app.modules.products.service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
        data: ProductCreate,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin)
):
    """Create product with category (only admin)."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    product = await service.create_product(data)

    await session.commit()
    await session.refresh(product, attribute_names=["category"])

    return product


@router.get("/", response_model=list[ProductRead])
async def list_products(
        session: AsyncSession = Depends(get_session),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        include_inactive: bool = Query(False, description="Include inactive products")
):
    """List all products.

    Returns all products from the database. No authentication required.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_inactive: Whether to include inactive products

    Returns:
        list[ProductRead]: List of all products
    """

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.get_list_products(skip, limit, include_inactive)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
        product_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Get a specific product by ID.

    Args:
        product_id: ID of the product to retrieve
        session: Database session

    Returns:
        ProductRead: Requested product

    Raises:
        HTTPException: 404 if product not found
    """

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.get_product_by_id(product_id)


@router.delete(
    "/{product_id}",
    summary="Delete product",
)
async def delete_product(
        product_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """Delete item by id."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    await service.delete_product(product_id)
    await session.commit()
    return {"status": "deleted"}


@router.patch(
    "/{product_id}/deactivate",
    summary="Update product to deactivate",
)
async def product_to_deactivate(
        product_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """deactivate item by id."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    await service.deactivate_product(product_id)
    await session.commit()
    return {"status": "deactivate"}


@router.patch(
    "/{product_id}/activate",
    summary="Update product to activate",
)
async def product_to_activate(
        product_id: int,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin),
):
    """activate item by id."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    await service.activate_product(product_id)
    await session.commit()
    return {"status": "activate"}


@router.get(
    "/by-category/{category_id}",
    response_model=list[ProductRead],
    summary="Get products by category",
)
async def list_products_by_category(
        category_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        include_subcategories: bool = Query(
            False,
            description="Include products from all subcategories"
        ),
        session: AsyncSession = Depends(get_session),
):
    """Get list of all products in selected category.

    Args:
        category_id: ID of the category
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_subcategories: If True, include products from all subcategories
        session: Database session

    Returns:
        list[ProductRead]: List of products in the category
    """

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.list_category_products(
        category_id,
        skip,
        limit,
        include_subcategories
    )


@router.get(
    "/by-category/{category_id}/count",
    summary="Get products count in category",
)
async def count_products_by_category(
        category_id: int,
        include_subcategories: bool = Query(
            False,
            description="Include products from all subcategories"
        ),
        session: AsyncSession = Depends(get_session),
):
    """Get count of products in a category.

    Args:
        category_id: ID of the category
        include_subcategories: If True, include products from subcategories
        session: Database session

    Returns:
        dict: Category ID and products count
    """

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    count = await service.get_products_count_by_category(
        category_id,
        include_subcategories
    )

    return {
        "category_id": category_id,
        "products_count": count,
        "include_subcategories": include_subcategories
    }


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
        product_id: int,
        product_update: ProductUpdate,
        session: AsyncSession = Depends(get_session),
        admin=Depends(get_current_admin)
):
    """Update product information."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.update_product(product_id, product_update)


@router.get("/filter/", response_model=list[ProductFilter])
async def get_products(
        filters: ProductFilterParams = Depends(),
        session: AsyncSession = Depends(get_session),
):
    """Get products with filtering and pagination.

    Supports filtering by:
    - search (name or description)
    - min_price / max_price
    - category_id (with optional include_subcategories)
    """

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.get_products(filters)
