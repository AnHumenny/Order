from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate


class ProductService:

    def __init__(self, repo: ProductRepository):
        self.repo = repo


    async def create_product(self, data: ProductCreate) -> Product:
        """Create product with category."""

        product_data = data.model_dump()
        product_data.pop("category", None)
        product = Product(**product_data)

        try:
            return await self.repo.create_with_category(product)

        except IntegrityError as e:
            await self.repo.session.rollback()

            if "foreign key" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category does not exist",
                )
            elif "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Product with this SKU/article already exists",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Database integrity error",
                )


    async def get_list_products(
            self,
            skip: int = 0,
            limit: int = 100,
    ) -> list[Product]:
        """Get list of all products."""
        return await self.repo.get_all(skip, limit)


    async def get_product_by_id(
            self,
            product_id: int,
    ) -> Product:
        """Get single product by id."""
        return await self.repo.get_product_by_id(product_id)


    async def delete_product(self, category_id: int):
        """Delete a category by ID with existence validation.

        Attempts to delete a category and verifies that the category
        actually existed. If the category doesn't exist, raises a 404 error.

        Args:
            category_id: ID of the category to delete

        Returns:
            None

        Raises:
            HTTPException: 404 Not Found if the category doesn't exist
        """

        deleted = await self.repo.delete(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )


    async def list_category_products(
            self,
            category_id,
            skip,
            limit
    ) -> list[Product]:
        """Get all products from selected categories."""
        return await self.repo.get_product_by_category(category_id, skip, limit)
