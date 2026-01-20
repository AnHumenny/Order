from unittest import skip

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from app.core.database import get_session
from app.core.dependencies import get_current_admin
from app.modules.products.schemas import ProductRead, ProductCreate
from app.modules.products.models import Product


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)

async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_session),
    admin = Depends(get_current_admin)
):
    """Create a new product (admin only).

    Creates a new product with provided data. Requires admin authentication.

    Args:
        data: ProductCreate schema with product details
        session: Database session
        admin: Admin user verification

    Returns:
        ProductRead: Created product

    Status:
        201: Product successfully created
        401: Unauthorized (not admin)
    """

    product_data = data.model_dump()

    if 'category' in product_data:
        del product_data['category']

    product = Product(**product_data)

    session.add(product)
    await session.commit()

    # Возвращаем без категории
    return product

@router.get("/", response_model=list[ProductRead])
async def list_products(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """List all products.

    Returns all products from the database. No authentication required.

    Args:
        session: Database session

    Returns:
        list[ProductRead]: List of all products
    """

    stmt = (
        select(Product)
        .options(selectinload(Product.category))
        .offset(skip)
        .limit(limit)
        .order_by(Product.id)
    )

    result = await session.execute(stmt)
    products = result.scalars().all()

    return products


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific product by ID.

    Args:
        product_id: ID of the product to retrieve
        session: Database session

    Returns:
        ProductRead: Requested product

    Raises:
        HTTPException: 404 if product not found
    """

    stmt = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product_id)
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product
