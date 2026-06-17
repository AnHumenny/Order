from fastapi import APIRouter, Depends, Response, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Optional
from app.core.database import get_session
from app.core.dependencies import get_current_user_optional, get_current_user
from app.core.rate_limiter import limiter, RateLimits
from app.core.session import get_or_create_session_id
from app.modules.cart.schemas import CartRead, CartItemRead, CartItemCreate, CartItemUpdate
from app.modules.cart.service import CartService
from app.modules.cart.repository import CartRepository
from app.modules.private_modules.auth.models import User

router = APIRouter(
    prefix="/cart",
)


@router.post("/items", response_model=CartRead)
@limiter.limit(RateLimits.WRITE)
async def add_to_cart(
        request: Request,
        response: Response,
        data: CartItemCreate,
        user: Optional[User] = Depends(get_current_user_optional),
        session: AsyncSession = Depends(get_session),
):
    """Add a product to cart (supports both auth and guest users).

    Args:
        request: FastAPI request object
        response: FastAPI response object
        data: CartItemCreate containing product_id and quantity
        user: Authenticated user (optional, from token)
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    session_id = get_or_create_session_id(request, response)

    service = CartService(CartRepository(session))

    if user:
        await service.add_item(user.id, data, session_id=None)
    else:
        await service.add_item(None, data, session_id=session_id)

    await session.commit()

    if user:
        cart = await service.get_cart(user_id=user.id, session_id=None)
    else:
        cart = await service.get_cart(user_id=None, session_id=session_id)

    if not cart or not cart.items:
        return CartRead(items=[], total_price=Decimal(0))

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.get("/", response_model=CartRead)
@limiter.limit(RateLimits.READ)
async def get_cart(
        request: Request,
        response: Response,
        user: Optional[User] = Depends(get_current_user_optional),
        session: AsyncSession = Depends(get_session),
):
    """Retrieve current cart (supports both auth and guest users).

    Args:
        request: FastAPI request object
        response: FastAPI response object
        user: Authenticated user (optional, from token)
        session: Database session

    Returns:
        CartRead: User's cart with items and total price
    """

    session_id = get_or_create_session_id(request, response)
    service = CartService(CartRepository(session))

    if user:
        cart = await service.get_cart(user_id=user.id, session_id=None)
    else:
        cart = await service.get_cart(user_id=None, session_id=session_id)

    if not cart or not cart.items:
        return CartRead(items=[], total_price=Decimal(0))

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.delete("/", response_model=CartRead)
@limiter.limit(RateLimits.WRITE)
async def clear_cart(
        request: Request,
        response: Response,
        user: Optional[User] = Depends(get_current_user_optional),
        session: AsyncSession = Depends(get_session),
):
    """Clear the current shopping cart (supports both auth and guest users).

    Removes all items from the cart.
    Returns an empty cart with zero total price upon successful completion.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        user: Authenticated user (optional, from token)
        session: Database session

    Returns:
        CartRead: Empty cart with zero total price
    """

    session_id = get_or_create_session_id(request, response)
    service = CartService(CartRepository(session))

    if user:
        await service.clear_cart_items(user.id, None)
    else:
        await service.clear_cart_items(None, session_id)

    await session.commit()

    return CartRead(items=[], total_price=Decimal(0))


@router.post("/product/{product_id}/increment", response_model=CartRead)
@limiter.limit(RateLimits.WRITE)
async def increment_product_quantity(
        request: Request,
        response: Response,
        product_id: int,
        user: Optional[User] = Depends(get_current_user_optional),
        session: AsyncSession = Depends(get_session),
):
    """Increment product quantity in cart by 1.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        product_id: ID of the product to increment
        user: Authenticated user (optional, from token)
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    session_id = get_or_create_session_id(request, response)
    service = CartService(CartRepository(session))

    if user:
        await service.increment_product_quantity(user.id, None, product_id)
    else:
        await service.increment_product_quantity(None, session_id, product_id)

    await session.commit()

    if user:
        cart = await service.get_cart(user_id=user.id, session_id=None)
    else:
        cart = await service.get_cart(user_id=None, session_id=session_id)

    if not cart or not cart.items:
        return CartRead(items=[], total_price=Decimal(0))

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.post("/product/{product_id}/decrement", response_model=CartRead)
@limiter.limit(RateLimits.WRITE)
async def decrement_product_quantity(
        request: Request,
        response: Response,
        product_id: int,
        user: Optional[User] = Depends(get_current_user_optional),
        session: AsyncSession = Depends(get_session),
):
    """Decrement product quantity in cart by 1.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        product_id: ID of the product to decrement
        user: Authenticated user (optional, from token)
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    session_id = get_or_create_session_id(request, response)
    service = CartService(CartRepository(session))

    if user:
        await service.decrement_product_quantity(user.id, None, product_id)
    else:
        await service.decrement_product_quantity(None, session_id, product_id)

    await session.commit()

    if user:
        cart = await service.get_cart(user_id=user.id, session_id=None)
    else:
        cart = await service.get_cart(user_id=None, session_id=session_id)

    if not cart or not cart.items:
        return CartRead(items=[], total_price=Decimal(0))

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.put("/product/{product_id}/quantity", response_model=CartRead)
@limiter.limit(RateLimits.WRITE)
async def update_product_quantity(
        request: Request,
        response: Response,
        product_id: int,
        data: CartItemUpdate,
        user: Optional[User] = Depends(get_current_user_optional),
        session: AsyncSession = Depends(get_session),
):
    """Update product quantity to specific value.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        product_id: ID of the product to update
        data: New quantity value (must be >= 1)
        user: Authenticated user (optional, from token)
        session: Database session

    Returns:
        CartRead: Updated cart with all items and total price
    """

    session_id = get_or_create_session_id(request, response)
    service = CartService(CartRepository(session))

    if user:
        await service.update_product_quantity(user.id, None, product_id, data.quantity)
    else:
        await service.update_product_quantity(None, session_id, product_id, data.quantity)

    await session.commit()

    if user:
        cart = await service.get_cart(user_id=user.id, session_id=None)
    else:
        cart = await service.get_cart(user_id=None, session_id=session_id)

    if not cart or not cart.items:
        return CartRead(items=[], total_price=Decimal(0))

    total_price = sum((item.price * item.quantity for item in cart.items), Decimal(0))

    return CartRead(
        items=[CartItemRead.model_validate(item) for item in cart.items],
        total_price=total_price
    )


@router.post("/merge")
@limiter.limit(RateLimits.READ)
async def merge_carts(
        request: Request,
        response: Response,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    """Merge guest cart into user cart after login.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        user: Authenticated user (required, from token)
        session: Database session

    Returns:
        dict: Success message with merged cart ID
    """

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="No guest cart to merge")

    service = CartService(CartRepository(session))

    user_cart = await service.merge_carts(user_id=user.id, session_id=session_id)
    await session.commit()

    response.delete_cookie("session_id")

    return {"message": "Carts merged successfully", "cart_id": user_cart.id}
