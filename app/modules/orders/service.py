from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.cart.service import CartService
from app.modules.orders.models import Order, OrderItem, OrderStatus
from app.modules.cart.repository import CartRepository
from app.modules.orders.repository import OrderRepository
from app.modules.payment.stripe_client import create_payment_intent


class OrderService:

    def __init__(self, order_repo: OrderRepository, cart_repo: CartRepository):
        self.order_repo = order_repo
        self.cart_repo = cart_repo


    async def create_from_cart(self, user_id: int) -> Order:
        session = self.order_repo.session
        print(f"[create_from_cart] START for user_id={user_id}")

        try:
            async with session.begin():
                print("[create_from_cart] Transaction BEGIN")

                cart = await self.cart_repo.get_cart_with_items(user_id)
                print(f"[create_from_cart] Cart loaded: {cart}")
                print(f"[create_from_cart] Cart items BEFORE clear: "
                      f"{[(i.product_id, i.quantity) for i in cart.items]}")

                if not cart or not cart.items:
                    print("[create_from_cart] Cart is empty, raising HTTPException")
                    raise HTTPException(400, "Cart is empty")

                order = Order(user_id=user_id)
                print("[create_from_cart] Order instance created")

                for item in cart.items:
                    order_item = OrderItem(
                        product_id=item.product_id,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                    order.items.append(order_item)
                    print(f"[create_from_cart] Added OrderItem: {item.product_id}, qty={item.quantity}")

                order.total_amount = calculate_order_total(order.items)
                print(f"[create_from_cart] Order total_amount calculated: {order.total_amount}")

                cart.items[:] = []
                print("[create_from_cart] Cart items cleared")

                await self.order_repo.create(order)
                print(f"[create_from_cart] Order persisted with id={order.id}")

            print("[create_from_cart] Transaction COMMIT successfully")

        except Exception as e:
            print(f"[create_from_cart] TRANSACTION FAILED: {e}")
            raise

        return order


def calculate_order_total(items: list[OrderItem]) -> int:
    """Returns the order amount in minimum units (cents)."""

    total = 0
    for item in items:
        total += int(item.price * 100) * item.quantity
    return total


async def checkout_cart(db: AsyncSession, user) -> dict:

    cart_repo = CartRepository(db)
    cart_service = CartService(cart_repo)

    cart_items = await cart_service.get_cart_items_for_checkout(user.id)

    if not cart_items:
        raise ValueError("Cart is empty")

    order = Order(
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_amount=0,
    )
    db.add(order)
    await db.flush()

    order_items = [
        OrderItem(
            order_id=order.id,
            product_id=item.product.id,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
        )
        for item in cart_items
    ]
    db.add_all(order_items)

    order.total_amount = calculate_order_total(order_items)
    await db.commit()

    amount_for_stripe: int = int(order.total_amount)
    intent = create_payment_intent(
        amount=amount_for_stripe,
        metadata={
            "order_id": str(order.id),
            "user_id": str(user.id),
        },

    )

    order.stripe_payment_intent_id = intent.id
    await db.commit()

    return {
        "order_id": order.id,
        "client_secret": intent.client_secret,
    }
