from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.core.database import get_session
from app.core.dependencies import get_current_admin
from app.core.rate_limiter import RateLimits, limiter
from app.modules.category.models import Category
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


@router.get("/search", response_model=List[ProductFilter])     #кэшировать часто повторяющиеся запросы?
@limiter.limit(RateLimits.READ)
async def search_products(
        request: Request,
        name: str = Query(..., min_length=2, max_length=100),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        only_active: bool = Query(True),
        session: AsyncSession = Depends(get_session)
):
    """Search for products by name."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    products = await service.search_products_by_name(
        name=name,
        skip=skip,
        limit=limit,
        only_active=only_active
    )
    return products


@router.get("/search/advanced", response_model=List[ProductFilter])
@limiter.limit(RateLimits.READ)
async def search_products_advanced(
        request: Request,
        search: str = Query(..., min_length=2, description="Поисковый запрос"),
        min_price: Optional[float] = Query(None, gt=0, description="Минимальная цена"),
        max_price: Optional[float] = Query(None, gt=0, description="Максимальная цена"),
        category_name: Optional[str] = Query(None, description="Название категории для поиска"),
        include_subcategories: bool = Query(False, description="Включая подкатегории"),
        skip: int = Query(0, ge=0, description="Сколько пропустить"),
        limit: int = Query(20, ge=1, le=100, description="Сколько вернуть"),
        session: AsyncSession = Depends(get_session)
):
    """Advanced product search with filtering.

    - **search**: Search by product name and description
    - **min_price**: Minimum price
    - **max_price**: Maximum price
    - **category_name**: Search by category name
    - **include_subcategories**: Include products from subcategories
    - **skip**: Pagination (how many to skip)
    - **limit**: Pagination (how many to return)
    """

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )

    category_id = None
    if category_name:
        result = await session.execute(
            select(Category.id).where(Category.name.ilike(f"%{category_name}%"))
        )
        category_id = result.scalar_one_or_none()

        if category_id is None:
            return []

    filters = ProductFilterParams(
        search=search,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        include_subcategories=include_subcategories,
        skip=skip,
        limit=limit,
        is_active=True
    )

    products = await service.search_products_advanced(filters)
    return products


@router.get("/search/with-count")
@limiter.limit(RateLimits.READ)
async def search_products_with_count(
        request: Request,
        name: str = Query(..., min_length=2),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        only_active: bool = Query(True),
        session: AsyncSession = Depends(get_session)
):
    """Search with counting quantity."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    products, total = await service.search_products_with_count(
        name=name,
        skip=skip,
        limit=limit,
        only_active=only_active
    )
    return {
        "items": products,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.get("/filter/", response_model=list[ProductFilter])
@limiter.limit(RateLimits.READ)
async def get_products(
        request: Request,
        filters: ProductFilterParams = Depends(),
        session: AsyncSession = Depends(get_session),
):
    """Get products with filtering and pagination."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.get_products(filters)


@router.get("/by-category/{category_id}", response_model=list[ProductRead])
@limiter.limit(RateLimits.READ)
async def list_products_by_category(
        request: Request,
        category_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        include_subcategories: bool = Query(False),
        session: AsyncSession = Depends(get_session),
):
    """Get list of all products in selected category."""

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


@router.get("/by-category/{category_id}/count")
@limiter.limit(RateLimits.READ)
async def count_products_by_category(
        request: Request,
        category_id: int,
        include_subcategories: bool = Query(False),
        session: AsyncSession = Depends(get_session),
):
    """Get count of products in a category."""

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


@router.get("/{product_id}", response_model=ProductRead)
@limiter.limit(RateLimits.READ)
async def get_product(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Get a specific product by ID."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.get_product_by_id(product_id)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.READ)
async def create_product(
        request: Request,
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
@limiter.limit(RateLimits.READ)
async def list_products(
        request: Request,
        session: AsyncSession = Depends(get_session),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        include_inactive: bool = Query(False)
):
    """List all products."""

    service = ProductService(
        ProductRepository(session),
        CategoryRepository(session)
    )
    return await service.get_list_products(skip, limit, include_inactive)


@router.delete("/{product_id}", summary="Delete product")
@limiter.limit(RateLimits.READ)
async def delete_product(
        request: Request,
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


@router.patch("/{product_id}/deactivate", summary="Update product to deactivate")
@limiter.limit(RateLimits.READ)
async def product_to_deactivate(
        request: Request,
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


@router.patch("/{product_id}/activate", summary="Update product to activate")
@limiter.limit(RateLimits.READ)
async def product_to_activate(
        request: Request,
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


@router.patch("/{product_id}", response_model=ProductRead)
@limiter.limit(RateLimits.READ)
async def update_product(
        request: Request,
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
