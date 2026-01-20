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
