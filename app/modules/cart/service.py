from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.modules.cart.schemas import CartRead, CartItemRead
from app.modules.cart.models import CartItem
from app.modules.products.models import Product


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
        """Add a product item to the user's shopping cart.

        Retrieves the product from the database, gets or creates the user's cart,
        and adds the product as a cart item. If the product already exists in the cart,
        increments its quantity instead of creating a duplicate entry.

        Args:
            user_id: ID of the user who owns the cart
            data: Object containing product details (must include product_id and quantity)

        Returns:
            None: The method modifies the cart in place and returns nothing
        """

        product = await self.repo.session.scalar(
            select(Product).where(Product.id == data.product_id)
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        cart = await self.repo.get_or_create_cart(user_id)

        for item in cart.items:
            if item.product_id == product.id:
                item.quantity += data.quantity
                return

        cart.items.append(
            CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=data.quantity,
       #         price=product.price,
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

        total_price = sum(
            (item.product.price * item.quantity for item in cart.items),
            Decimal("0.00")
        )

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


    async def get_cart_items_for_checkout(self, user_id: int) -> list[CartItem]:
        """Returns the CartItem of the model (NOT schemas)

        Used only for checkout
        """
        cart = await self.repo.get_cart_with_items(user_id)

        if not cart:
            return []

        return list(cart.items)


    async def clear_cart_items(self, user_id: int):
        """Removed all the items in the user's shopping cart"""
        await self.repo.clear_cart_items(user_id)


    async def update_product_quantity(self, user_id: int, product_id: int, new_quantity: int):
        """Update quantity of a specific product in user's cart.

        Finds the cart item by product ID for the given user and updates its quantity
        to the specified value. The operation is atomic and ensures data consistency.

        Args:
            user_id: ID of the user who owns the cart
            product_id: ID of the product whose quantity needs to be updated
            new_quantity: New quantity value to set (must be validated before calling)
        """

        cart_item = await self.repo.get_cart_item_by_product_for_user(user_id, product_id)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found in cart"
            )

        cart_item.quantity = new_quantity
        await self.repo.session.commit()


    async def remove_item(self, user_id: int, item_id: int):
        """Remove a specific item from cart.

        Args:
            user_id: ID of the cart owner
            item_id: ID of the cart item to remove

        Raises:
            HTTPException: If item not found
        """

        cart = await self.repo.get_cart_with_items(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )

        item_removed = False
        for i, item in enumerate(cart.items):
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


    async def increment_product_quantity(self, user_id: int, product_id: int):
        """Increment product quantity in cart by 1 using product_id.

        Args:
            user_id: ID of the cart owner
            product_id: ID of the product to increment

        Raises:
            HTTPException: If product not found in cart
        """

        cart = await self.repo.get_cart_with_items(user_id)
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


    async def decrement_product_quantity(self, user_id: int, product_id: int):
        """Decrement product quantity in cart by 1 using product_id.

        Args:
            user_id: ID of the cart owner
            product_id: ID of the product to decrement

        Raises:
            HTTPException: If product not found in cart
        """

        cart = await self.repo.get_cart_with_items(user_id)
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
