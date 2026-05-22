from decimal import Decimal
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user, get_current_admin
from app.core.rate_limiter import limiter, RateLimits
from app.modules.orders.models import Order, OrderStatus
from app.modules.orders.schemas import OrderRead
from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService, checkout_cart
from app.modules.cart.repository import CartRepository
from fastapi import APIRouter, Depends, HTTPException, Request

from app.modules.private_modules.auth.models import User

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/from-cart", response_model=OrderRead)
@limiter.limit(RateLimits.WRITE)
async def create_order(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new order from the user's current cart.

    Converts the authenticated user's shopping cart into a new order.
    The order will contain all items currently in the cart, and the cart
    will typically be cleared after order creation.

    Authentication is required.
    """

    service = OrderService(
        OrderRepository(session),
        CartRepository(session),
    )

    order = await service.create_from_cart(user.id)

    total_price = sum(
        Decimal(item.price) * item.quantity for item in order.items
    )

    return OrderRead(
        id=order.id,
        status=order.status,
        created_at=order.created_at,
        items=order.items,
        total_price=total_price,
    )


@router.post("/checkout")
@limiter.limit(RateLimits.WRITE)
async def checkout(
    request: Request,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    """Process cart checkout for authenticated user.

    Returns checkout details or 400 error if cart is empty/invalid.
    """

    try:
        return await checkout_cart(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/my")
@limiter.limit(RateLimits.WRITE)
async def delete_my_pending_orders(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    admin = Depends(get_current_admin),
):
    """Delete all pending orders for the current user (admin only).

    Removes all orders with PENDING status belonging to the authenticated user.
    This operation requires admin privileges.

    Args:
        user: Current authenticated user (obtained via get_current_user dependency)
        session: Async database session
        admin: Admin user object (obtained via get_current_admin dependency)
    """

    result = await session.execute(
        delete(Order).where(
            Order.user_id == user.id,
            Order.status == OrderStatus.PENDING
        )
    )

    await session.commit()

    deleted_count = result.rowcount if hasattr(result, 'rowcount') else 0

    return {
        "detail": "Pending orders deleted",
        "deleted": deleted_count
    }
