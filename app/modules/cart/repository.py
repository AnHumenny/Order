from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.modules.cart.models import Cart, CartItem


class CartRepository:
    """Repository for cart-related database operations.

    Handles all database interactions for shopping carts and cart items.
    Provides methods for cart creation, retrieval, and item management.
    Supports both authenticated users and guests (via session_id).

    Args:
        session: SQLAlchemy async database session
    """

    def __init__(self, session):
        self.session = session

    async def get_or_create_cart(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> Cart:
        """Get existing cart or create a new one.

        If a cart doesn't exist for the given user_id or session_id,
        creates a new cart. Ensures each user or session has exactly one cart.

        Args:
            user_id: ID of the authenticated user (optional)
            session_id: Session ID for guest users (optional)

        Returns:
            Cart: The cart (existing or newly created)

        Raises:
            ValueError: If neither user_id nor session_id is provided
        """

        if user_id is None and session_id is None:
            raise ValueError("Either user_id or session_id must be provided")

        conditions = []
        if user_id is not None:
            conditions.append(Cart.user_id == user_id)
        if session_id is not None:
            conditions.append(Cart.session_id == session_id)

        stmt = (
            select(Cart)
            .where(or_(*conditions))
            .options(selectinload(Cart.items))
        )
        cart = await self.session.scalar(stmt)

        if not cart:
            cart = Cart(
                user_id=user_id,
                session_id=session_id if user_id is None else None
            )
            self.session.add(cart)
            await self.session.flush()

        return cart


    async def get_cart_with_items(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> Cart | None:
        """Get cart with all items and product details loaded.

        Efficiently loads cart with all items and their associated product
        information using eager loading. Can search by user_id or session_id.

        Args:
            user_id: ID of the authenticated user (optional)
            session_id: Session ID for guest users (optional)

        Returns:
            Cart | None: The cart with items and products loaded, or None if not found
        """

        if user_id is None and session_id is None:
            return None

        conditions = []
        if user_id is not None:
            conditions.append(Cart.user_id == user_id)
        if session_id is not None:
            conditions.append(Cart.session_id == session_id)

        stmt = (
            select(Cart)
            .where(or_(*conditions))
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product)
            )
        )

        return await self.session.scalar(stmt)


    async def clear_cart_items(
            self,
            cart_id: Optional[int] = None,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> None:
        """Clear all items from a cart.

        This method retrieves the cart and removes all associated cart items
        from the database. If no cart exists, the method returns
        without performing any operations.

        Args:
            cart_id: Direct cart ID (optional)
            user_id: ID of the authenticated user (optional)
            session_id: Session ID for guest users (optional)
        """

        if cart_id:
            await self.session.execute(
                delete(CartItem).where(CartItem.cart_id == cart_id)
            )
        else:
            cart = await self.get_cart_with_items(user_id, session_id)
            if not cart:
                return

            await self.session.execute(
                delete(CartItem).where(CartItem.cart_id == cart.id)
            )

        await self.session.commit()


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


    async def get_cart_item_by_id_for_user(
            self,
            user_id: int,
            item_id: int
    ) -> CartItem | None:
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

    async def get_cart_item_by_product(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None,
            product_id: int = None
    ) -> CartItem | None:
        """Get cart item by product ID for either user or guest.

        Args:
            user_id: ID of the authenticated user (optional)
            session_id: Session ID for guest users (optional)
            product_id: ID of the product to find

        Returns:
            CartItem | None: The cart item if found, None otherwise
        """

        if user_id is None and session_id is None:
            return None

        cart = await self.get_cart_with_items(user_id, session_id)
        if not cart:
            return None

        for item in cart.items:
            if item.product_id == product_id:
                return item

        return None


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
        await self.session.flush()
        return result.rowcount > 0


    async def delete_cart(self, cart_id: int) -> bool:
        """Delete a cart by its ID.

        This will cascade delete all cart items due to cascade="all, delete-orphan".

        Args:
            cart_id: ID of the cart to delete

        Returns:
            bool: True if cart was deleted, False if not found
        """

        result = await self.session.execute(
            delete(Cart).where(Cart.id == cart_id)
        )
        await self.session.flush()
        return result.rowcount > 0


    async def get_cart_items_count(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> int:
        """Get the number of items in cart.

        Args:
            user_id: ID of the authenticated user (optional)
            session_id: Session ID for guest users (optional)

        Returns:
            int: Total number of items in cart
        """

        cart = await self.get_cart_with_items(user_id, session_id)
        if not cart:
            return 0
        return len(cart.items)


    async def get_cart_total_quantity(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> int:
        """Get the total quantity of all items in cart.

        Args:
            user_id: ID of the authenticated user (optional)
            session_id: Session ID for guest users (optional)

        Returns:
            int: Sum of all item quantities in cart
        """

        cart = await self.get_cart_with_items(user_id, session_id)
        if not cart:
            return 0
        return sum(item.quantity for item in cart.items)


    async def get_cart_item_by_product_for_user(
            self,
            user_id: int,
            product_id: int
    ) -> CartItem | None:
        """Get cart item by product ID ensuring it belongs to the user.

        Legacy method for backward compatibility.
        Use get_cart_item_by_product instead.

        Args:
            user_id: ID of the authenticated user
            product_id: ID of the product to find

        Returns:
            CartItem | None: The cart item if found and belongs to user, None otherwise
        """

        return await self.session.scalar(
            select(CartItem)
            .join(Cart)
            .where(
                CartItem.product_id == product_id,
                Cart.user_id == user_id
            )
            .options(selectinload(CartItem.product))
        )


    async def get_or_create_cart_by_session(
            self,
            session_id: str
    ) -> Cart:
        """Get existing cart by session_id or create new one.

        Convenience method for guest users.

        Args:
            session_id: Session ID for guest user

        Returns:
            Cart: The cart (existing or newly created)
        """

        return await self.get_or_create_cart(session_id=session_id)


    async def transfer_cart_to_user(
            self,
            session_id: str,
            user_id: int
    ) -> Cart | None:
        """Transfer a guest cart to a registered user.

        This method finds the guest cart by session_id and reassigns it to the user.
        If the user already has a cart, items will be merged (should be handled in service).

        Args:
            session_id: Session ID of the guest cart
            user_id: ID of the user to transfer the cart to

        Returns:
            Cart | None: The transferred cart or None if not found
        """

        cart = await self.get_cart_with_items(session_id=session_id)
        if not cart:
            return None

        cart.user_id = user_id
        cart.session_id = None
        await self.session.flush()

        return cart
