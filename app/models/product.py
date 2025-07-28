"""Product and category models."""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductCategory(Base):
    """Product category model."""
    
    __tablename__ = "product_categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id}, name='{self.name}')>"


class Product(Base):
    """Product model for pharmacy items."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    generic_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    brand_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Product identification
    barcode: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    ndc_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # National Drug Code
    
    # Product details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dosage_form: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # tablet, capsule, liquid, etc.
    strength: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 500mg, 10ml, etc.
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Pricing
    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    markup_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Inventory settings
    min_stock_level: Mapped[int] = mapped_column(Integer, default=10)
    max_stock_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reorder_point: Mapped[int] = mapped_column(Integer, default=5)
    
    # Pharmacy-specific
    requires_prescription: Mapped[bool] = mapped_column(Boolean, default=False)
    is_controlled_substance: Mapped[bool] = mapped_column(Boolean, default=False)
    controlled_substance_schedule: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_discontinued: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Foreign keys
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_categories.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="products")
    inventory_batches: Mapped[List["InventoryBatch"]] = relationship("InventoryBatch", back_populates="product")
    sale_items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="product")
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
