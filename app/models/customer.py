"""Customer model for pharmacy POS system."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    """Customer model for pharmacy customers."""
    
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Personal information
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    
    # Address information
    address_line1: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="USA")
    
    # Medical information
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medical_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Insurance information
    insurance_provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    insurance_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    insurance_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Loyalty program
    loyalty_card_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    
    # Preferences
    preferred_contact_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # email, phone, sms
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    prescription_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_visit: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="customer")
    
    @property
    def full_name(self) -> str:
        """Get customer's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """Calculate customer's age from date of birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.full_name}', email='{self.email}')>"
