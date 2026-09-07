from datetime import datetime
from decimal import Decimal
from typing import Any, Coroutine

from app.modules.analytics.repository import AnalyticsRepository


class AnalyticsService:
    """Service for business logic analytics"""

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository


    async def get_user_purchase_analytics(
            self,
            user_id: int
    ) -> dict[str, dict[str, list[str] | list[int] | list[Decimal]]]:
        """Get analytics on user purchases for the current year"""
        current_year = datetime.now().year

        orders = await self.repository.get_user_orders_by_year(user_id, current_year)

        if not orders:
            return {
                "products": {"labels": [], "data": []},
                "sums": {"labels": [], "data": []}
            }

        order_ids = [order.id for order in orders]
        items = await self.repository.get_order_items(order_ids)

        product_ids = [item.product_id for item in items]
        products = await self.repository.get_products_by_ids(product_ids)

        product_counts: dict[str, int] = {}
        product_sums: dict[str, Decimal] = {}

        for item in items:
            product = products.get(item.product_id)
            if not product:
                continue

            name = product.name

            product_counts[name] = product_counts.get(name, 0) + item.quantity
            product_sums[name] = (
                    product_sums.get(name, Decimal("0"))
                    + item.price * item.quantity
            )

        top_by_count = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        top_by_sum = sorted(product_sums.items(), key=lambda x: x[1], reverse=True)[:6]

        return {
            "products": {
                "labels": [item[0] for item in top_by_count],
                "data": [item[1] for item in top_by_count]
            },
            "sums": {
                "labels": [item[0] for item in top_by_sum],
                "data": [item[1] for item in top_by_sum]
            }
        }


    async def get_user_stats(self, user_id: int) -> dict[str, int | float]:
        """Get user statistics (total orders and amount)"""
        orders = await self.repository.get_all_user_orders(user_id)

        total_orders = len(orders)
        total_spent = sum(order.total_amount for order in orders)

        return {
            "total_orders": total_orders,
            "total_spent": float(total_spent)
        }
