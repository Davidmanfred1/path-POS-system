"""Product management service."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductCategory
from app.models.inventory import InventoryBatch


class ProductService:
    """Service for managing products and categories."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_data: dict) -> Product:
        """Create a new product."""
        product = Product(**product_data)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID with inventory batches."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.inventory_batches))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        result = await self.db.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get product by barcode."""
        result = await self.db.execute(
            select(Product).where(Product.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def search_products(
        self,
        query: str,
        category_id: Optional[int] = None,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Product]:
        """Search products by name, generic name, or brand name."""
        conditions = []

        # Text search
        search_conditions = [
            Product.name.ilike(f"%{query}%"),
            Product.generic_name.ilike(f"%{query}%"),
            Product.brand_name.ilike(f"%{query}%"),
            Product.sku.ilike(f"%{query}%")
        ]
        conditions.append(or_(*search_conditions))

        # Category filter
        if category_id:
            conditions.append(Product.category_id == category_id)

        # Active filter
        if active_only:
            conditions.append(Product.is_active == True)

        result = await self.db.execute(
            select(Product)
            .where(and_(*conditions))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_products(
        self,
        category_id: Optional[int] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get all products with pagination."""
        conditions = []

        if category_id:
            conditions.append(Product.category_id == category_id)

        if active_only:
            conditions.append(Product.is_active == True)

        query = select(Product)
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_product(self, product_id: int, update_data: dict) -> Optional[Product]:
        """Update product information."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return None

        for key, value in update_data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> bool:
        """Soft delete a product (mark as inactive)."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return False

        product.is_active = False
        await self.db.commit()
        return True

    async def get_low_stock_products(self, threshold_multiplier: float = 1.0) -> List[Product]:
        """Get products with low stock levels."""
        # This will be implemented with inventory service
        # For now, return products where current stock is below reorder point
        result = await self.db.execute(
            select(Product)
            .join(InventoryBatch)
            .where(
                and_(
                    Product.is_active == True,
                    InventoryBatch.current_quantity <= Product.reorder_point * threshold_multiplier
                )
            )
        )
        return result.scalars().all()

    # Category management methods
    async def create_category(self, category_data: dict) -> ProductCategory:
        """Create a new product category."""
        category = ProductCategory(**category_data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_all_categories(self, active_only: bool = True) -> List[ProductCategory]:
        """Get all product categories."""
        conditions = []
        if active_only:
            conditions.append(ProductCategory.is_active == True)

        query = select(ProductCategory)
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: int) -> Optional[ProductCategory]:
        """Get category by ID."""
        result = await self.db.execute(
            select(ProductCategory).where(ProductCategory.id == category_id)
        )
        return result.scalar_one_or_none()
