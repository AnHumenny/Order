from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.modules.cart.schemas import CartRead, CartItemRead, CartItemCreate, CartItemUpdate
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


@router.post("/product/{product_id}/increment", response_model=CartRead)
async def increment_product_quantity(
        product_id: int,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    """Increment product quantity in cart by 1.

    Args:
        product_id: ID of the product to increment (matches the product_id from cart response)
        user: Authenticated user
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    service = CartService(CartRepository(session))
    await service.increment_product_quantity(user.id, product_id)
    await session.commit()

    cart = await service.get_cart(user.id)
    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.post("/product/{product_id}/decrement", response_model=CartRead)
async def decrement_product_quantity(
        product_id: int,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    """Decrement product quantity in cart by 1.

    Args:
        product_id: ID of the product to decrement (matches the product_id from cart response)
        user: Authenticated user
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    service = CartService(CartRepository(session))
    await service.decrement_product_quantity(user.id, product_id)
    await session.commit()

    cart = await service.get_cart(user.id)
    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.put("/product/{product_id}/quantity", response_model=CartRead)
async def update_product_quantity(
        product_id: int,
        data: CartItemUpdate,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    """Update product quantity to specific value.

    Args:
        product_id: ID of the product to update
        data: New quantity value (must be >= 1)
        user: Authenticated user
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    service = CartService(CartRepository(session))
    await service.update_product_quantity(user.id, product_id, data.quantity)
    await session.commit()

    cart = await service.get_cart(user.id)
    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )
