import logging
from typing import List, Tuple
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status
from app.modules.category.repository import CategoryRepository
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductFilterParams, ProductFilter


class ProductService:
    """Service layer for product business logic with category hierarchy support."""

    def __init__(self, repo: ProductRepository, category_repo: CategoryRepository):
        self.repo = repo
        self.category_repo = category_repo

    async def create_product(self, data: ProductCreate) -> Product:
        """Create product with category validation."""

        category = await self.category_repo.get_by_id(data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {data.category_id} does not exist"
            )

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
            include_inactive: bool = False
    ) -> list[Product]:
        """Get list of all products."""
        return await self.repo.get_all(skip, limit, include_inactive)

    async def get_product_by_id(
            self,
            product_id: int,
    ) -> Product:
        """Get single product by id."""
        return await self.repo.get_product_by_id(product_id)

    async def delete_product(self, product_id: int):
        """Delete a product by ID with existence and usage validation."""
        can_delete = await self.repo.can_delete_product(product_id)
        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete product because it exists in orders or carts",
            )

        deleted = await self.repo.delete(product_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )

    async def deactivate_product(self, product_id: int):
        """Deactivate a product by ID."""
        deactivate = await self.repo.deactivate(product_id)

        if not deactivate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

    async def activate_product(self, product_id: int):
        """Activate a product by ID."""
        activate = await self.repo.activate(product_id)

        if not activate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

    async def list_category_products(
            self,
            category_id: int,
            skip: int = 0,
            limit: int = 100,
            include_subcategories: bool = False
    ) -> list[Product]:
        """Get all products from selected categories.

        Args:
            category_id: ID of the category
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_subcategories: If True, include products from all subcategories

        Returns:
            list[Product]: List of products
        """

        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        if include_subcategories:
            category_ids = await self.category_repo.get_category_tree_ids(category_id)
            return await self.repo.get_products_by_categories(category_ids, skip, limit)
        else:
            return await self.repo.get_product_by_category(category_id, skip, limit)

    async def update_product(self, product_id: int, update_data: ProductUpdate) -> Product:
        """Update product with validation and transaction management."""

        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        if 'name' in update_dict:
            if not update_dict['name'] or not update_dict['name'].strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product name cannot be empty"
                )

        if 'category_id' in update_dict and update_dict['category_id'] is not None:
            category = await self.category_repo.get_by_id(update_dict['category_id'])
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with id {update_dict['category_id']} does not exist"
                )

        try:
            updated_product = await self.repo.update(product_id, update_dict)
            await self.repo.session.commit()
            return updated_product

        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Database integrity error"
            )

        except Exception as e:
            await self.repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating product: {str(e)}"
            )

    async def get_products(self, filters: ProductFilterParams) -> List[dict]:
        """Get a list of products with filtering.

        Supports filtering by category with subcategories option.
        """
        category_ids = None

        if filters.category_id:
            if filters.include_subcategories:
                category_ids = await self.category_repo.get_category_tree_ids(filters.category_id)
            else:
                category_ids = [filters.category_id]

        products = await self.repo.get_all_with_filters(
            search=filters.search,
            min_price=filters.min_price,
            max_price=filters.max_price,
            category_ids=category_ids,
            is_active=filters.is_active,
            skip=filters.skip,
            limit=filters.limit
        )
        return products

    async def get_products_by_category_tree(
            self,
            category_ids: List[int],
            skip: int = 0,
            limit: int = 100
    ) -> list[Product]:
        """Get products from multiple categories."""
        return await self.repo.get_products_by_categories(category_ids, skip, limit)

    async def get_products_count_by_category(
            self,
            category_id: int,
            include_subcategories: bool = False
    ) -> int:
        """Get count of products in a category.

        Args:
            category_id: ID of the category
            include_subcategories: If True, include products from all subcategories

        Returns:
            int: Number of products
        """

        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        if include_subcategories:
            category_ids = await self.category_repo.get_category_tree_ids(category_id)
            return await self.repo.count_products_by_categories(category_ids)
        else:
            return await self.repo.count_products_by_category(category_id)

    async def get_products_with_category_path(self, product_id: int) -> dict:
        """Get product with full category path."""

        product = await self.get_product_by_id(product_id)

        if product.category_id:
            category_path = await self.category_repo.get_category_path(product.category_id)
            path_string = " > ".join([c.name for c in category_path]) if category_path else None
        else:
            category_path = []
            path_string = None

        return {
            "product": product,
            "category_path": category_path,
            "category_path_string": path_string
        }


    async def search_products_by_name(
            self,
            name: str,
            skip: int = 0,
            limit: int = 20,
            only_active: bool = True
    ) -> List[ProductFilter]:
        """Search products by name."""

        try:
            products = await self.repo.search_by_name(
                name=name,
                skip=skip,
                limit=limit,
                only_active=only_active
            )

            result = []
            for product in products:
                main_image_url = None
                has_images = False

                if product.images and len(product.images) > 0:
                    has_images = True
                    main_img = next((img for img in product.images if img.is_main), None)
                    if main_img:
                        main_image_url = main_img.image_url
                    else:
                        main_image_url = product.images[0].image_url

                result.append(ProductFilter(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price=float(product.price),
                    category_id=product.category_id,
                    category_name=product.category.name if product.category else None,
                    is_active=product.is_active,
                    has_images=has_images,
                    main_image_url=main_image_url
                ))

            return result

        except Exception as e:
            logging.error(f"Search error: {e}")
            return []


    async def search_products_with_count(
            self,
            name: str,
            skip: int = 0,
            limit: int = 20,
            only_active: bool = True
    ) -> Tuple[List[Product], int]:
        """Search products and return total count."""

        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters long"
            )

        return await self.repo.search_by_name_with_count(
            name=name.strip(),
            skip=skip,
            limit=limit,
            only_active=only_active
        )

    async def search_products_advanced(
            self,
            filters: ProductFilterParams
    ) -> list[dict]:
        """Advanced product search using filters.

        Supports:
            - Search by title and description (search)
            - Filtering by price (min_price, max_price)
            - Filtering by category with subcategories (category_id, include_subcategories)
            - Filtering by activity (is_active)
            - Pagination (skip, limit)
        """

        if filters.search and len(filters.search.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters long"
            )

        if filters.min_price and filters.max_price:
            if filters.min_price > filters.max_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="min_price cannot be greater than max_price"
                )

        category_ids = None
        if filters.category_id:
            if filters.include_subcategories:
                category_ids = await self.category_repo.get_category_tree_ids(filters.category_id)
                if not category_ids:
                    category_ids = [filters.category_id]
            else:
                category_ids = [filters.category_id]

        products = await self.repo.get_all_with_filters(
            search=filters.search,
            min_price=filters.min_price,
            max_price=filters.max_price,
            category_ids=category_ids,
            is_active=filters.is_active,
            skip=filters.skip,
            limit=filters.limit
        )

        return products

    async def search_products_advanced_with_count(
            self,
            filters: ProductFilterParams
    ) -> Tuple[List[Product], int]:
        """Advanced product search with total quantity calculation."""

        if filters.search and len(filters.search.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters long"
            )

        if filters.min_price and filters.max_price:
            if filters.min_price > filters.max_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="min_price cannot be greater than max_price"
                )

        category_ids = None
        if filters.category_id:
            if filters.include_subcategories:
                category_ids = await self.category_repo.get_category_tree_ids(filters.category_id)
                if not category_ids:
                    category_ids = [filters.category_id]
            else:
                category_ids = [filters.category_id]

        products, total = await self.repo.get_all_with_filters_and_count(
            search=filters.search,
            min_price=filters.min_price,
            max_price=filters.max_price,
            category_ids=category_ids,
            is_active=filters.is_active,
            skip=filters.skip,
            limit=filters.limit
        )

        return products, total
