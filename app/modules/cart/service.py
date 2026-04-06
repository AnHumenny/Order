from decimal import Decimal
from typing import Optional
from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from app.modules.cart.schemas import CartRead, CartItemRead
from app.modules.products.models import Product
from app.modules.cart.models import CartItem


class CartService:
    """Service layer for cart business logic.

    Handles cart operations and business rules, separating concerns from
    the repository (data access) and API layer (HTTP handling).
    Supports both authenticated users and guests (via session_id).

    Args:
        repo: CartRepository instance for data access
    """

    def __init__(self, repo):
        self.repo = repo

    async def add_item(
            self,
            user_id: Optional[int],
            data,
            session_id: Optional[str] = None
    ):
        """Add item to cart for either user or guest.

        Args:
            user_id: ID of authenticated user (optional)
            data: CartItemCreate schema with product_id and quantity
            session_id: Session ID for guest users (optional)

        Raises:
            HTTPException: If product not found
        """

        product = await self.repo.session.scalar(
            select(Product).where(Product.id == data.product_id)
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        cart = await self.repo.get_or_create_cart(user_id, session_id)

        stmt = select(CartItem).where(CartItem.cart_id == cart.id)
        result = await self.repo.session.scalars(stmt)
        items_list = result.all()

        existing_item = None
        for item in items_list:
            if item.product_id == product.id:
                existing_item = item
                break

        if existing_item:
            existing_item.quantity += data.quantity
        else:
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=data.quantity,
            )
            self.repo.session.add(new_item)

        await self.repo.session.commit()


    async def get_cart(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> CartRead:
        """Get cart formatted for API response.

        Retrieves cart with all items and calculates total price.
        Returns empty cart if cart doesn't exist.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)

        Returns:
            CartRead: Formatted cart data for API response
        """

        cart = await self.repo.get_cart_with_items(user_id, session_id)

        if not cart or not cart.items:
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

    async def get_cart_items_for_checkout(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ) -> list[CartItem]:
        """Returns the CartItem of the model (NOT schemas)

        Used only for checkout. Supports both authenticated users and guests.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)

        Returns:
            list[CartItem]: List of cart items or empty list if no cart
        """

        cart = await self.repo.get_cart_with_items(user_id, session_id)

        if not cart:
            return []

        return list(cart.items)


    async def clear_cart_items(
            self,
            user_id: Optional[int] = None,
            session_id: Optional[str] = None
    ):
        """Remove all items from the shopping cart.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)
        """

        cart = await self.repo.get_cart_with_items(user_id, session_id)
        if cart:
            await self.repo.clear_cart_items(cart.id)


    async def update_product_quantity(
            self,
            user_id: Optional[int],
            session_id: Optional[str],
            product_id: int,
            new_quantity: int
    ):
        """Update quantity of a specific product in cart.

        Finds the cart item by product ID and updates its quantity
        to the specified value. Supports both authenticated users and guests.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)
            product_id: ID of the product whose quantity needs to be updated
            new_quantity: New quantity value to set (must be >= 1)

        Raises:
            HTTPException: If product not found in cart
        """

        cart_item = await self.repo.get_cart_item_by_product(
            user_id, session_id, product_id
        )

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found in cart"
            )

        cart_item.quantity = new_quantity
        await self.repo.session.commit()


    async def remove_item(
            self,
            user_id: Optional[int],
            session_id: Optional[str],
            item_id: int
    ):
        """Remove a specific item from cart by its ID.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)
            item_id: ID of the cart item to remove

        Raises:
            HTTPException: If cart or item not found
        """

        cart = await self.repo.get_cart_with_items(user_id, session_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )

        item_removed = False
        for item in cart.items:
            if item.id == item_id:
                await self.repo.session.delete(item)
                item_removed = True
                break

        if not item_removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart"
            )

        await self.repo.session.commit()


    async def increment_product_quantity(
            self,
            user_id: Optional[int],
            session_id: Optional[str],
            product_id: int
    ):
        """Increment product quantity in cart by 1 using product_id.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)
            product_id: ID of the product to increment

        Raises:
            HTTPException: If product not found in cart
        """

        cart = await self.repo.get_cart_with_items(user_id, session_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )

        cart_item = None
        for item in cart.items:
            if item.product_id == product_id:
                cart_item = item
                break

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found in cart"
            )

        cart_item.quantity += 1
        await self.repo.session.commit()


    async def decrement_product_quantity(
            self,
            user_id: Optional[int],
            session_id: Optional[str],
            product_id: int
    ):
        """Decrement product quantity in cart by 1 using product_id.

        If quantity becomes 0, removes the item from cart.

        Args:
            user_id: ID of authenticated user (optional)
            session_id: Session ID for guest users (optional)
            product_id: ID of the product to decrement

        Raises:
            HTTPException: If product not found in cart
        """

        cart = await self.repo.get_cart_with_items(user_id, session_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )

        cart_item = None
        for item in cart.items:
            if item.product_id == product_id:
                cart_item = item
                break

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found in cart"
            )

        if cart_item.quantity <= 1:
            await self.repo.session.delete(cart_item)
        else:
            cart_item.quantity -= 1

        await self.repo.session.commit()


    async def merge_carts(
            self,
            user_id: int,
            session_id: str
    ):
        """Merge guest cart into user cart after login.

        Transfers all items from guest cart to user cart.
        If same product exists in both carts, quantities are summed.
        Guest cart is deleted after merge.

        Args:
            user_id: ID of authenticated user
            session_id: Session ID of the guest cart

        Returns:
            Cart: The merged user cart
        """

        guest_cart = await self.repo.get_cart_with_items(session_id=session_id)

        if not guest_cart:
            return await self.repo.get_or_create_cart(user_id=user_id)

        user_cart = await self.repo.get_or_create_cart(user_id=user_id)

        for guest_item in guest_cart.items:
            existing_item = None
            for user_item in user_cart.items:
                if user_item.product_id == guest_item.product_id:
                    existing_item = user_item
                    break

            if existing_item:
                existing_item.quantity += guest_item.quantity
            else:
                new_item = CartItem(
                    cart_id=user_cart.id,
                    product_id=guest_item.product_id,
                    quantity=guest_item.quantity
                )
                self.repo.session.add(new_item)

        await self.repo.delete_cart(guest_cart.id)
        await self.repo.session.commit()

        return user_cart
