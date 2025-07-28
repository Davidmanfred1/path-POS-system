"""Inventory management service for tracking stock movements and batches."""

from datetime import datetime, date
from typing import List, Optional, Dict
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.inventory import InventoryBatch, StockMovement, MovementType
from app.models.user import User


class InventoryService:
    """Service for managing inventory batches and stock movements."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_inventory_batch(
        self,
        product_id: int,
        batch_data: Dict
    ) -> InventoryBatch:
        """Create a new inventory batch."""
        batch = InventoryBatch(
            product_id=product_id,
            **batch_data
        )
        
        # Set current quantity to initial quantity
        batch.current_quantity = batch.initial_quantity
        
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        
        # Record initial stock movement
        await self.record_stock_movement(
            product_id=product_id,
            batch_id=batch.id,
            quantity=batch.initial_quantity,
            movement_type=MovementType.PURCHASE,
            user_id=1,  # System user - should be passed as parameter
            unit_cost=batch.cost_per_unit,
            notes=f"Initial stock for batch {batch.batch_number}"
        )
        
        return batch
    
    async def get_batch_by_id(self, batch_id: int) -> Optional[InventoryBatch]:
        """Get inventory batch by ID."""
        result = await self.db.execute(
            select(InventoryBatch)
            .options(selectinload(InventoryBatch.product))
            .where(InventoryBatch.id == batch_id)
        )
        return result.scalar_one_or_none()
    
    async def get_product_batches(
        self,
        product_id: int,
        active_only: bool = True,
        available_only: bool = False
    ) -> List[InventoryBatch]:
        """Get all batches for a product."""
        conditions = [InventoryBatch.product_id == product_id]
        
        if active_only:
            conditions.append(InventoryBatch.is_active == True)
        
        if available_only:
            conditions.append(InventoryBatch.current_quantity > 0)
        
        result = await self.db.execute(
            select(InventoryBatch)
            .where(and_(*conditions))
            .order_by(InventoryBatch.expiry_date)
        )
        return result.scalars().all()
    
    async def get_available_stock(self, product_id: int) -> int:
        """Get total available stock for a product across all batches."""
        result = await self.db.execute(
            select(func.sum(InventoryBatch.current_quantity))
            .where(
                and_(
                    InventoryBatch.product_id == product_id,
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > 0
                )
            )
        )
        total = result.scalar()
        return total or 0
    
    async def reserve_stock(
        self,
        product_id: int,
        quantity: int,
        prefer_fifo: bool = True
    ) -> List[Dict]:
        """Reserve stock for a sale (FIFO by default)."""
        # Get available batches
        order_by = (
            InventoryBatch.expiry_date if prefer_fifo 
            else desc(InventoryBatch.expiry_date)
        )
        
        result = await self.db.execute(
            select(InventoryBatch)
            .where(
                and_(
                    InventoryBatch.product_id == product_id,
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > InventoryBatch.reserved_quantity
                )
            )
            .order_by(order_by)
        )
        batches = result.scalars().all()
        
        reservations = []
        remaining_quantity = quantity
        
        for batch in batches:
            if remaining_quantity <= 0:
                break
            
            available = batch.current_quantity - batch.reserved_quantity
            if available <= 0:
                continue
            
            reserve_qty = min(remaining_quantity, available)
            batch.reserved_quantity += reserve_qty
            remaining_quantity -= reserve_qty
            
            reservations.append({
                'batch_id': batch.id,
                'batch_number': batch.batch_number,
                'quantity': reserve_qty,
                'unit_price': batch.selling_price_per_unit,
                'expiry_date': batch.expiry_date
            })
        
        if remaining_quantity > 0:
            # Not enough stock available
            # Rollback reservations
            for reservation in reservations:
                batch = next(b for b in batches if b.id == reservation['batch_id'])
                batch.reserved_quantity -= reservation['quantity']
            raise ValueError(f"Insufficient stock. Need {quantity}, available {quantity - remaining_quantity}")
        
        await self.db.commit()
        return reservations
    
    async def release_reservation(self, reservations: List[Dict]) -> None:
        """Release stock reservations."""
        for reservation in reservations:
            batch = await self.get_batch_by_id(reservation['batch_id'])
            if batch:
                batch.reserved_quantity = max(0, batch.reserved_quantity - reservation['quantity'])
        
        await self.db.commit()
    
    async def confirm_sale(
        self,
        reservations: List[Dict],
        user_id: int,
        sale_reference: str
    ) -> None:
        """Confirm sale and update stock quantities."""
        for reservation in reservations:
            batch = await self.get_batch_by_id(reservation['batch_id'])
            if not batch:
                continue
            
            # Update quantities
            batch.current_quantity -= reservation['quantity']
            batch.reserved_quantity -= reservation['quantity']
            
            # Record stock movement
            await self.record_stock_movement(
                product_id=batch.product_id,
                batch_id=batch.id,
                quantity=-reservation['quantity'],
                movement_type=MovementType.SALE,
                user_id=user_id,
                reference_number=sale_reference,
                notes=f"Sale from batch {batch.batch_number}"
            )
        
        await self.db.commit()
    
    async def record_stock_movement(
        self,
        product_id: int,
        quantity: int,
        movement_type: MovementType,
        user_id: int,
        batch_id: Optional[int] = None,
        unit_cost: Optional[Decimal] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> StockMovement:
        """Record a stock movement for audit trail."""
        movement = StockMovement(
            product_id=product_id,
            batch_id=batch_id,
            quantity=quantity,
            movement_type=movement_type,
            user_id=user_id,
            unit_cost=unit_cost,
            reference_number=reference_number,
            notes=notes
        )
        
        self.db.add(movement)
        await self.db.commit()
        await self.db.refresh(movement)
        return movement
    
    async def adjust_stock(
        self,
        batch_id: int,
        new_quantity: int,
        user_id: int,
        reason: str
    ) -> bool:
        """Adjust stock quantity for a batch."""
        batch = await self.get_batch_by_id(batch_id)
        if not batch:
            return False
        
        old_quantity = batch.current_quantity
        adjustment = new_quantity - old_quantity
        
        batch.current_quantity = new_quantity
        
        # Record adjustment movement
        await self.record_stock_movement(
            product_id=batch.product_id,
            batch_id=batch_id,
            quantity=adjustment,
            movement_type=MovementType.ADJUSTMENT,
            user_id=user_id,
            notes=f"Stock adjustment: {reason}. Old: {old_quantity}, New: {new_quantity}"
        )
        
        await self.db.commit()
        return True
    
    async def get_stock_movements(
        self,
        product_id: Optional[int] = None,
        batch_id: Optional[int] = None,
        movement_type: Optional[MovementType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[StockMovement]:
        """Get stock movements with filters."""
        conditions = []
        
        if product_id:
            conditions.append(StockMovement.product_id == product_id)
        
        if batch_id:
            conditions.append(StockMovement.batch_id == batch_id)
        
        if movement_type:
            conditions.append(StockMovement.movement_type == movement_type)
        
        if start_date:
            conditions.append(StockMovement.created_at >= start_date)
        
        if end_date:
            conditions.append(StockMovement.created_at <= end_date)
        
        query = select(StockMovement).options(
            selectinload(StockMovement.product),
            selectinload(StockMovement.batch),
            selectinload(StockMovement.user)
        )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.db.execute(
            query.order_by(desc(StockMovement.created_at)).limit(limit)
        )
        return result.scalars().all()
    
    async def get_inventory_summary(self) -> Dict:
        """Get inventory summary statistics."""
        # Total products with stock
        result = await self.db.execute(
            select(func.count(func.distinct(InventoryBatch.product_id)))
            .where(
                and_(
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > 0
                )
            )
        )
        products_in_stock = result.scalar() or 0
        
        # Total inventory value
        result = await self.db.execute(
            select(func.sum(InventoryBatch.current_quantity * InventoryBatch.cost_per_unit))
            .where(
                and_(
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > 0
                )
            )
        )
        total_cost_value = result.scalar() or 0
        
        result = await self.db.execute(
            select(func.sum(InventoryBatch.current_quantity * InventoryBatch.selling_price_per_unit))
            .where(
                and_(
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > 0
                )
            )
        )
        total_selling_value = result.scalar() or 0
        
        # Low stock products
        result = await self.db.execute(
            select(func.count(func.distinct(Product.id)))
            .join(InventoryBatch)
            .where(
                and_(
                    Product.is_active == True,
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity <= Product.reorder_point
                )
            )
        )
        low_stock_products = result.scalar() or 0
        
        return {
            'products_in_stock': products_in_stock,
            'total_cost_value': float(total_cost_value),
            'total_selling_value': float(total_selling_value),
            'potential_profit': float(total_selling_value - total_cost_value),
            'low_stock_products': low_stock_products
        }
