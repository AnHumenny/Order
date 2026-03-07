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
        """Clear all items from a user's shopping cart.

        This method retrieves the user's cart and removes all associated cart items
        from the database. If no cart exists for the given user, the method returns
        without performing any operations.
        """

        cart = await self.get_cart_with_items(user_id)
        if not cart:
            return

        await self.session.execute(
            delete(CartItem).where(CartItem.cart_id == cart.id)
        )


    async def get_cart_item_by_id(self, item_id: int) -> CartItem | None:
        """Get a specific cart item by its ID.

        Args:
            item_id: ID of the cart item to retrieve

        Returns:
            CartItem | None: The cart item if found, None otherwise
        """

        return await self.session.scalar(
            select(CartItem)
            .where(CartItem.id == item_id)
            .options(selectinload(CartItem.product))
        )


    async def get_cart_item_by_id_for_user(self, user_id: int, item_id: int) -> CartItem | None:
        """Get a specific cart item ensuring it belongs to the user.

        This method verifies that the cart item exists and belongs to the
        specified user by joining through the cart relationship.

        Args:
            user_id: ID of the user who should own the item
            item_id: ID of the cart item to retrieve

        Returns:
            CartItem | None: The cart item if found and belongs to user, None otherwise
        """

        return await self.session.scalar(
            select(CartItem)
            .join(Cart)
            .where(
                CartItem.id == item_id,
                Cart.user_id == user_id
            )
            .options(selectinload(CartItem.product))
        )


    async def update_item_quantity(self, item_id: int, new_quantity: int) -> CartItem | None:
        """Update quantity of a cart item.

        Args:
            item_id: ID of the cart item to update
            new_quantity: New quantity value

        Returns:
            CartItem | None: The updated cart item if found, None otherwise
        """

        cart_item = await self.session.get(CartItem, item_id)
        if cart_item:
            cart_item.quantity = new_quantity
            await self.session.flush()
        return cart_item


    async def delete_cart_item(self, item_id: int) -> bool:
        """Delete a cart item by its ID.

        Args:
            item_id: ID of the cart item to delete

        Returns:
            bool: True if item was deleted, False if not found
        """

        result = await self.session.execute(
            delete(CartItem).where(CartItem.id == item_id)
        )
        return result.rowcount > 0


    async def get_cart_items_count(self, user_id: int) -> int:
        """Get the number of items in user's cart.

        Args:
            user_id: ID of the user

        Returns:
            int: Total number of items in cart
        """

        cart = await self.get_cart_with_items(user_id)
        if not cart:
            return 0
        return len(cart.items)


    async def get_cart_total_quantity(self, user_id: int) -> int:
        """Get the total quantity of all items in user's cart.

        Args:
            user_id: ID of the user

        Returns:
            int: Sum of all item quantities in cart
        """

        cart = await self.get_cart_with_items(user_id)
        if not cart:
            return 0
        return sum(item.quantity for item in cart.items)


    async def get_cart_item_by_product_for_user(self, user_id: int, product_id: int) -> CartItem | None:
        """Get cart item by product ID ensuring it belongs to the user."""

        return await self.session.scalar(
            select(CartItem)
            .join(Cart)
            .where(
                CartItem.product_id == product_id,
                Cart.user_id == user_id
            )
            .options(selectinload(CartItem.product))
        )
