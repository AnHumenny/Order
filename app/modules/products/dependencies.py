from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.products.repository import ProductRepository
from app.modules.category.repository import CategoryRepository
from app.modules.products.service import ProductService

async def get_product_service(
    session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[ProductService, None]:
    """Dependency for ProductService with scoped repositories."""

    product_repo = ProductRepository(session)
    category_repo = CategoryRepository(session)
    service = ProductService(product_repo, category_repo)
    try:
        yield service
    finally:
        pass
