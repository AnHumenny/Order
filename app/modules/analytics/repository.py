from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract
from app.modules.orders.models import Order, OrderItem
from app.modules.products.models import Product
from typing import Optional


class AnalyticsRepository:
    """Repository for working with analytics data"""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_user_orders_by_year(self, user_id: int, year: int, status: str = 'paid'):
        """Get user orders for the specified year"""

        query = select(Order).where(
            Order.user_id == user_id,
            extract('year', Order.created_at) == year,
            Order.status == status
        )
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_order_items(self, order_ids: list[int]):
        """Get all order items by list of order IDs"""
        query = select(OrderItem).where(OrderItem.order_id.in_(order_ids))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_products_by_ids(self, product_ids: list[int]):
        """Get products by list ID"""
        query = select(Product).where(Product.id.in_(product_ids))
        result = await self.session.execute(query)
        return {p.id: p for p in result.scalars().all()}


    async def get_all_user_orders(self, user_id: int, statuses: Optional[list[str]] = None):
        """Get all user orders with specific statuses"""
        if statuses is None:
            statuses = ['paid', 'completed', 'delivered']

        query = select(Order).where(
            Order.user_id == user_id,
            Order.status.in_(statuses)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
