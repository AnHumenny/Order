from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.users.models import User
from app.modules.orders.schemas import OrderRead, OrderItemRead
from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService
from app.modules.cart.repository import CartRepository


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/from-cart", response_model=OrderRead)
async def create_order(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Convert the user's shopping cart into an order.

    Creates a new order containing all items from the user's cart,
    then clears the cart. Transaction ensures atomicity.

    Args:
        user: Authenticated user (from token)
        session: Database session

    Returns:
        OrderRead: The created order with items and total price
    """

    async with session.begin():
        service = OrderService(
            OrderRepository(session),
            CartRepository(session),
        )
        order = await service.create_from_cart(user.id)

    total_price = sum(
        (item.price * item.quantity for item in order.items),
        Decimal("0.00")
    )

    return OrderRead(
        id=order.id,
        status=order.status,
        created_at=order.created_at,
        items=[OrderItemRead.model_validate(item) for item in order.items],
        total_price=total_price,
    )
