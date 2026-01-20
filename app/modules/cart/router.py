from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.modules.cart.schemas import CartRead, CartItemRead, CartItemCreate
from app.modules.cart.service import CartService
from app.modules.cart.repository import CartRepository
from app.users.models import User

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post("/items", response_model=CartRead)
async def add_to_cart(
    data: CartItemCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Add a product to the user's shopping cart.

    Endpoint restricted to admin users only. Adds specified quantity of a product
    to the cart. If product already exists in cart, updates the quantity.

    Args:
        data: CartItemRead containing product_id and quantity
        user: Authenticated user (from token)
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    service = CartService(CartRepository(session))
    await service.add_item(user.id, data)
    await session.commit()

    cart = await service.get_cart(user.id)

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.get("/", response_model=CartRead)
async def get_cart(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Retrieve the current user's shopping cart.

    Returns the cart with all items and calculates the total price.

    Args:
        user: Authenticated user (from token)
        session: Database session

    Returns:
        CartRead: User's cart with items and total price
    """

    service = CartService(CartRepository(session))
    cart = await service.get_cart(user.id)

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )

@router.delete("/", response_model=CartRead)
async def clear_cart(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Clear the current user's shopping cart.

    Removes all items from the authenticated user's cart.
    Returns an empty cart with zero total price upon successful completion.

    Authentication is required.
    """

    service = CartService(CartRepository(session))
    await service.clear_cart_items(user.id)
    await session.commit()

    return CartRead(items=[], total_price=Decimal(0))
