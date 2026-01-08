from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.modules.cart.models import Cart, CartItem


class CartRepository:
    """Repository for cart-related database operations.

    Handles all database interactions for shopping carts and cart items.
    Provides methods for cart creation, retrieval, and item management.

    Args:
        session: SQLAlchemy async database session"""

    def __init__(self, session):
        self.session = session


    async def get_or_create_cart(self, user_id: int) -> Cart:
        """Get existing cart or create a new one for the user.

        If a cart doesn't exist for the given user, creates a new cart.
        Ensures each user has exactly one cart.

        Args:
            user_id: ID of the user to get/create cart for

        Returns:
            Cart: The user's cart (existing or newly created)
        """

        result = await self.session.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            await self.session.flush()

        return cart


    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        """Get user's cart with all items and product details loaded.

        Efficiently loads cart with all items and their associated product
        information using eager loading.

        Args:
            user_id: ID of the user whose cart to retrieve

        Returns:
            Cart | None: The cart with items and products loaded, or None if not found
        """
        return await self.session.scalar(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product)
            )
        )

    async def clear_cart_items(self, user_id: int) -> None:
        cart = await self.get_cart_with_items(user_id)
        if not cart:
            return

        await self.session.execute(
            delete(CartItem).where(CartItem.cart_id == cart.id)
        )