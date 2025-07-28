"""Inventory and stock management models."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Numeric, Boolean, DateTime, Date, ForeignKey, Integer, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class MovementType(str, enum.Enum):
    """Types of stock movements."""
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    EXPIRED = "expired"
    DAMAGED = "damaged"
    TRANSFER = "transfer"


class InventoryBatch(Base):
    """Inventory batch model for tracking products with expiry dates."""
    
    __tablename__ = "inventory_batches"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_number: Mapped[str] = mapped_column(String(50), index=True)
    lot_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Quantities
    initial_quantity: Mapped[int] = mapped_column(Integer)
    current_quantity: Mapped[int] = mapped_column(Integer)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    # Pricing for this batch
    cost_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    selling_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    # Dates
    manufacture_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, index=True)
    received_date: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Supplier information
    supplier_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    purchase_order_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign keys
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_batches")
    stock_movements: Mapped[List["StockMovement"]] = relationship("StockMovement", back_populates="batch")
    
    @property
    def available_quantity(self) -> int:
        """Get available quantity (current - reserved)."""
        return self.current_quantity - self.reserved_quantity
    
    @property
    def days_until_expiry(self) -> int:
        """Get number of days until expiry."""
        return (self.expiry_date - date.today()).days
    
    def __repr__(self) -> str:
        return f"<InventoryBatch(id={self.id}, batch='{self.batch_number}', qty={self.current_quantity})>"


class StockMovement(Base):
    """Stock movement tracking for audit trail."""
    
    __tablename__ = "stock_movements"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType))
    quantity: Mapped[int] = mapped_column(Integer)  # Positive for in, negative for out
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Reference information
    reference_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Sale ID, PO number, etc.
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign keys
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("inventory_batches.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product")
    batch: Mapped[Optional["InventoryBatch"]] = relationship("InventoryBatch", back_populates="stock_movements")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<StockMovement(id={self.id}, type='{self.movement_type}', qty={self.quantity})>"
