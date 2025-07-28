"""Point of Sale service for handling transactions and cart management."""

from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.user import User
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService


@dataclass
class CartItem:
    """Cart item data structure."""
    product_id: int
    product_name: str
    sku: str
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal = Decimal('0.00')
    prescription_number: Optional[str] = None
    prescriber_name: Optional[str] = None
    days_supply: Optional[int] = None
    
    @property
    def line_total(self) -> Decimal:
        """Calculate line total after discount."""
        subtotal = self.quantity * self.unit_price
        return subtotal - self.discount_amount
    
    @property
    def discount_percentage(self) -> Decimal:
        """Calculate discount percentage."""
        if self.unit_price == 0:
            return Decimal('0.00')
        subtotal = self.quantity * self.unit_price
        return (self.discount_amount / subtotal * 100).quantize(Decimal('0.01'))


@dataclass
class Cart:
    """Shopping cart for POS transactions."""
    items: List[CartItem] = field(default_factory=list)
    customer_id: Optional[int] = None
    discount_amount: Decimal = Decimal('0.00')
    tax_rate: Decimal = Decimal('0.00')
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate cart subtotal."""
        return sum(item.line_total for item in self.items)
    
    @property
    def total_discount(self) -> Decimal:
        """Calculate total discount amount."""
        item_discounts = sum(item.discount_amount for item in self.items)
        return item_discounts + self.discount_amount
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        taxable_amount = self.subtotal - self.discount_amount
        return (taxable_amount * self.tax_rate / 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    @property
    def total(self) -> Decimal:
        """Calculate cart total."""
        return self.subtotal - self.discount_amount + self.tax_amount
    
    @property
    def item_count(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    def add_item(self, cart_item: CartItem) -> None:
        """Add item to cart or update quantity if exists."""
        existing_item = self.find_item(cart_item.product_id)
        if existing_item:
            existing_item.quantity += cart_item.quantity
        else:
            self.items.append(cart_item)
    
    def remove_item(self, product_id: int) -> bool:
        """Remove item from cart."""
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                del self.items[i]
                return True
        return False
    
    def update_item_quantity(self, product_id: int, quantity: int) -> bool:
        """Update item quantity."""
        item = self.find_item(product_id)
        if item:
            if quantity <= 0:
                return self.remove_item(product_id)
            item.quantity = quantity
            return True
        return False
    
    def find_item(self, product_id: int) -> Optional[CartItem]:
        """Find item in cart by product ID."""
        for item in self.items:
            if item.product_id == product_id:
                return item
        return None
    
    def clear(self) -> None:
        """Clear all items from cart."""
        self.items.clear()
        self.customer_id = None
        self.discount_amount = Decimal('0.00')


class POSService:
    """Service for Point of Sale operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.product_service = ProductService(db)
        self._carts: Dict[str, Cart] = {}  # Session-based carts
    
    def get_cart(self, session_id: str) -> Cart:
        """Get or create cart for session."""
        if session_id not in self._carts:
            self._carts[session_id] = Cart()
        return self._carts[session_id]
    
    async def add_to_cart(
        self,
        session_id: str,
        product_id: int,
        quantity: int,
        prescription_info: Optional[Dict] = None
    ) -> Cart:
        """Add product to cart."""
        # Get product details
        product = await self.product_service.get_product_by_id(product_id)
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        
        # Check stock availability
        available_stock = await self.inventory_service.get_available_stock(product_id)
        if available_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {available_stock}, Requested: {quantity}")
        
        # Create cart item
        cart_item = CartItem(
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            quantity=quantity,
            unit_price=product.selling_price,
            prescription_number=prescription_info.get('prescription_number') if prescription_info else None,
            prescriber_name=prescription_info.get('prescriber_name') if prescription_info else None,
            days_supply=prescription_info.get('days_supply') if prescription_info else None
        )
        
        # Add to cart
        cart = self.get_cart(session_id)
        cart.add_item(cart_item)
        
        return cart
    
    async def remove_from_cart(self, session_id: str, product_id: int) -> Cart:
        """Remove product from cart."""
        cart = self.get_cart(session_id)
        cart.remove_item(product_id)
        return cart
    
    async def update_cart_item(
        self,
        session_id: str,
        product_id: int,
        quantity: int
    ) -> Cart:
        """Update cart item quantity."""
        if quantity > 0:
            # Check stock availability
            available_stock = await self.inventory_service.get_available_stock(product_id)
            if available_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {available_stock}, Requested: {quantity}")
        
        cart = self.get_cart(session_id)
        cart.update_item_quantity(product_id, quantity)
        return cart
    
    async def apply_discount(
        self,
        session_id: str,
        discount_amount: Optional[Decimal] = None,
        discount_percentage: Optional[Decimal] = None,
        product_id: Optional[int] = None
    ) -> Cart:
        """Apply discount to cart or specific item."""
        cart = self.get_cart(session_id)
        
        if product_id:
            # Apply discount to specific item
            item = cart.find_item(product_id)
            if not item:
                raise ValueError("Product not found in cart")
            
            if discount_amount:
                item.discount_amount = discount_amount
            elif discount_percentage:
                subtotal = item.quantity * item.unit_price
                item.discount_amount = (subtotal * discount_percentage / 100).quantize(Decimal('0.01'))
        else:
            # Apply discount to entire cart
            if discount_amount:
                cart.discount_amount = discount_amount
            elif discount_percentage:
                cart.discount_amount = (cart.subtotal * discount_percentage / 100).quantize(Decimal('0.01'))
        
        return cart
    
    async def set_customer(self, session_id: str, customer_id: int) -> Cart:
        """Set customer for cart."""
        # Verify customer exists
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise ValueError("Customer not found")
        
        cart = self.get_cart(session_id)
        cart.customer_id = customer_id
        return cart
    
    async def process_sale(
        self,
        session_id: str,
        payment_method: PaymentMethod,
        amount_paid: Decimal,
        cashier_id: int,
        payment_reference: Optional[str] = None,
        insurance_info: Optional[Dict] = None
    ) -> Sale:
        """Process the sale transaction."""
        cart = self.get_cart(session_id)
        
        if not cart.items:
            raise ValueError("Cart is empty")
        
        if amount_paid < cart.total:
            raise ValueError("Insufficient payment amount")
        
        # Generate sale number
        sale_number = await self._generate_sale_number()
        
        # Reserve stock for all items
        reservations = []
        try:
            for item in cart.items:
                item_reservations = await self.inventory_service.reserve_stock(
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                reservations.extend(item_reservations)
            
            # Create sale record
            sale = Sale(
                sale_number=sale_number,
                subtotal=cart.subtotal,
                tax_amount=cart.tax_amount,
                discount_amount=cart.total_discount,
                total_amount=cart.total,
                payment_method=payment_method,
                payment_reference=payment_reference,
                amount_paid=amount_paid,
                change_given=amount_paid - cart.total,
                customer_id=cart.customer_id,
                cashier_id=cashier_id,
                status=SaleStatus.COMPLETED,
                completed_at=datetime.utcnow()
            )
            
            # Add insurance information if provided
            if insurance_info:
                sale.insurance_claim_number = insurance_info.get('claim_number')
                sale.insurance_copay = insurance_info.get('copay')
                sale.insurance_coverage = insurance_info.get('coverage')
            
            self.db.add(sale)
            await self.db.flush()  # Get sale ID
            
            # Create sale items
            reservation_index = 0
            for item in cart.items:
                # Find corresponding reservations for this item
                item_reservations = []
                for _ in range(item.quantity):
                    if reservation_index < len(reservations):
                        item_reservations.append(reservations[reservation_index])
                        reservation_index += 1
                
                # Create sale item (simplified - using first reservation for batch info)
                first_reservation = item_reservations[0] if item_reservations else None
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    discount_amount=item.discount_amount,
                    line_total=item.line_total,
                    prescription_number=item.prescription_number,
                    prescriber_name=item.prescriber_name,
                    days_supply=item.days_supply,
                    batch_number=first_reservation['batch_number'] if first_reservation else None,
                    inventory_batch_id=first_reservation['batch_id'] if first_reservation else None
                )
                self.db.add(sale_item)
            
            # Confirm stock movements
            await self.inventory_service.confirm_sale(
                reservations=reservations,
                user_id=cashier_id,
                sale_reference=sale_number
            )
            
            # Update customer loyalty points if applicable
            if cart.customer_id:
                await self._update_customer_loyalty(cart.customer_id, cart.total)
            
            await self.db.commit()
            
            # Clear cart
            cart.clear()
            
            return sale
            
        except Exception as e:
            # Release reservations on error
            if reservations:
                await self.inventory_service.release_reservation(reservations)
            raise e
    
    async def _generate_sale_number(self) -> str:
        """Generate unique sale number."""
        today = datetime.now()
        prefix = f"POS{today.strftime('%Y%m%d')}"
        
        # Get last sale number for today
        result = await self.db.execute(
            select(Sale.sale_number)
            .where(Sale.sale_number.like(f"{prefix}%"))
            .order_by(Sale.sale_number.desc())
            .limit(1)
        )
        last_sale = result.scalar_one_or_none()
        
        if last_sale:
            # Extract sequence number and increment
            sequence = int(last_sale[-4:]) + 1
        else:
            sequence = 1
        
        return f"{prefix}{sequence:04d}"
    
    async def _update_customer_loyalty(self, customer_id: int, amount: Decimal) -> None:
        """Update customer loyalty points and total spent."""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if customer:
            # Add loyalty points (1 point per dollar spent)
            points_earned = int(amount)
            customer.loyalty_points += points_earned
            customer.total_spent += amount
            customer.last_visit = datetime.utcnow()
    
    def clear_cart(self, session_id: str) -> None:
        """Clear cart for session."""
        if session_id in self._carts:
            self._carts[session_id].clear()
