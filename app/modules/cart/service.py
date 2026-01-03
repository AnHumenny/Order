from decimal import Decimal
from app.modules.cart.schemas import CartRead, CartItemRead
from app.modules.cart.models import CartItem


class CartService:
    """Service layer for cart business logic.

    Handles cart operations and business rules, separating concerns from
    the repository (data access) and API layer (HTTP handling).

    Args:
        repo: CartRepository instance for data access
    """

    def __init__(self, repo):
        self.repo = repo


    async def add_item(self, user_id: int, data):
        """Add a product to user's cart or update quantity if already present.

        Business logic:
        1. Get or create user's cart
        2. If product already in cart, increase quantity
        3. Otherwise, add new cart item

        Args:
            user_id: ID of the cart owner
            data: CartItemCreate with product_id and quantity"""

        cart = await self.repo.get_or_create_cart(user_id)

        for item in cart.items:
            if item.product_id == data.product_id:
                item.quantity += data.quantity
                return

        cart.items.append(
            CartItem(
                product_id=data.product_id,
                quantity=data.quantity,
            )
        )


    async def get_cart(self, user_id: int) -> CartRead:
        """Get user's cart formatted for API response.

        Retrieves cart with all items and calculates total price.
        Returns empty cart if user doesn't have one.

        Args:
            user_id: ID of the cart owner

        Returns:
            CartRead: Formatted cart data for API response
        """

        cart = await self.repo.get_cart_with_items(user_id)

        if not cart:
            return CartRead(items=[], total_price=Decimal("0.00"))

        items: list[CartItemRead] = []

        total_price = Decimal("0.00")

        for item in cart.items:
            items.append(
                CartItemRead(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price,
                )
            )
            total_price += item.product.price * item.quantity

        return CartRead(
            items=items,
            total_price=total_price,
        )
