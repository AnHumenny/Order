from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.core.database import get_session
from app.core.dependencies import get_current_admin
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductRead, ProductCreate, ProductDelete
from app.modules.products.service import ProductService

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

    return await ProductService.create_product(
        data=data,
        session=session,
    )


@router.get("/", response_model=list[ProductRead])
async def list_products(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 20
):
    """List all products.

    Returns all products from the database. No authentication required.

    Args:
        session: Database session
        limit: int
        skip: int

    Returns:
        list[ProductRead]: List of all products
    """

    return await ProductService.list_products(
        session=session,
        skip=skip,
        limit=limit,
    )


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

    return await ProductService.get_product_by_id(
        product_id=product_id,
        session=session,
    )

@router.delete(
    "/{prodict_id}",
    summary="Delete product",
)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    """Delete item by id."""

    service = ProductService(ProductRepository(session))
    await service.delete_product(product_id)
    await session.commit()
    return {"status": "deleted"}


@router.get(
    "/categories/{category_id}/products",
    response_model=list[ProductRead],
)
async def list_products_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    """Get list of all items in selected category."""
    return await ProductService.list_category_products(
        session=session,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )
