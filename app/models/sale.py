"""Sales and transaction models."""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class PaymentMethod(str, enum.Enum):
    """Payment methods."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    INSURANCE = "insurance"
    CHECK = "check"
    GIFT_CARD = "gift_card"
    STORE_CREDIT = "store_credit"


class SaleStatus(str, enum.Enum):
    """Sale status."""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Sale(Base):
    """Sales transaction model."""
    
    __tablename__ = "sales"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sale_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
    # Financial information
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    # Payment information
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    change_given: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    
    # Insurance information (if applicable)
    insurance_claim_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    insurance_copay: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    insurance_coverage: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Status and metadata
    status: Mapped[SaleStatus] = mapped_column(Enum(SaleStatus), default=SaleStatus.PENDING)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    receipt_printed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Foreign keys
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), nullable=True)
    cashier_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="sales")
    cashier: Mapped["User"] = relationship("User")
    sale_items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, number='{self.sale_number}', total={self.total_amount})>"


class SaleItem(Base):
    """Individual items in a sale."""
    
    __tablename__ = "sale_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Item details
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    # Prescription information (if applicable)
    prescription_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    prescriber_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    days_supply: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    refills_remaining: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Batch tracking
    batch_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Foreign keys
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    inventory_batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("inventory_batches.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sale: Mapped["Sale"] = relationship("Sale", back_populates="sale_items")
    product: Mapped["Product"] = relationship("Product", back_populates="sale_items")
    inventory_batch: Mapped[Optional["InventoryBatch"]] = relationship("InventoryBatch")
    
    def __repr__(self) -> str:
        return f"<SaleItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"
