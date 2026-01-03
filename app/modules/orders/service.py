from fastapi import HTTPException
from app.modules.orders.models import Order, OrderItem
from app.modules.cart.repository import CartRepository
from app.modules.orders.repository import OrderRepository


class OrderService:
    """Service layer for order business logic.

    Handles order creation and management, coordinating between
    cart and order repositories.

    Args:
        order_repo: Repository for order data access
        cart_repo: Repository for cart data access
    """
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo


    async def create_from_cart(self, user_id: int) -> Order:
        """
        Convert user's cart into a new order.

        Business logic:
        1. Get user's cart with items
        2. Validate cart is not empty
        3. Create order with cart items as order items
        4. Clear the cart
        5. Persist the order

        Args:
            user_id: ID of the user placing the order

        Returns:
            Order: The created order

        Raises:
            HTTPException: 400 if cart is empty
        """
        cart = await self.cart_repo.get_cart_with_items(user_id)

        if not cart or not cart.items:
            raise HTTPException(400, "Cart is empty")

        order = Order(user_id=user_id)

        for item in cart.items:
            order.items.append(
                OrderItem(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                )
            )

        del cart.items[:]

        await self.order_repo.create(order)
        return order
