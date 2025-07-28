"""Intelligent expiry management and alert service for pharmacy products."""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.inventory import InventoryBatch
from app.config import get_settings


class ExpiryAlertLevel(str, Enum):
    """Expiry alert severity levels."""
    CRITICAL = "critical"    # 1 week or less
    HIGH = "high"           # 1 month or less
    MEDIUM = "medium"       # 3 months or less
    LOW = "low"             # 6 months or less
    INFO = "info"           # More than 6 months


@dataclass
class ExpiryAlert:
    """Expiry alert data structure."""
    batch_id: int
    product_id: int
    product_name: str
    batch_number: str
    current_quantity: int
    expiry_date: date
    days_until_expiry: int
    alert_level: ExpiryAlertLevel
    estimated_value: float
    recommended_action: str
    priority_score: float


class ExpiryService:
    """Service for managing product expiry alerts and recommendations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
    
    def _calculate_alert_level(self, days_until_expiry: int) -> ExpiryAlertLevel:
        """Calculate alert level based on days until expiry."""
        if days_until_expiry <= self.settings.expiry_alert_1_week:
            return ExpiryAlertLevel.CRITICAL
        elif days_until_expiry <= self.settings.expiry_alert_1_month:
            return ExpiryAlertLevel.HIGH
        elif days_until_expiry <= self.settings.expiry_alert_3_months:
            return ExpiryAlertLevel.MEDIUM
        elif days_until_expiry <= self.settings.expiry_alert_6_months:
            return ExpiryAlertLevel.LOW
        else:
            return ExpiryAlertLevel.INFO
    
    def _calculate_priority_score(
        self, 
        days_until_expiry: int, 
        quantity: int, 
        unit_value: float,
        is_controlled: bool = False
    ) -> float:
        """Calculate priority score for expiry alerts (higher = more urgent)."""
        # Base urgency score (inverse of days)
        urgency_score = max(0, 365 - days_until_expiry) / 365
        
        # Value impact score
        total_value = quantity * unit_value
        value_score = min(total_value / 1000, 1.0)  # Normalize to max 1.0
        
        # Quantity impact score
        quantity_score = min(quantity / 100, 1.0)  # Normalize to max 1.0
        
        # Controlled substance multiplier
        controlled_multiplier = 1.5 if is_controlled else 1.0
        
        # Weighted combination
        priority_score = (
            urgency_score * 0.5 +
            value_score * 0.3 +
            quantity_score * 0.2
        ) * controlled_multiplier
        
        return round(priority_score, 3)
    
    def _get_recommended_action(
        self, 
        days_until_expiry: int, 
        quantity: int,
        alert_level: ExpiryAlertLevel
    ) -> str:
        """Get recommended action based on expiry timeline and quantity."""
        if alert_level == ExpiryAlertLevel.CRITICAL:
            if quantity > 50:
                return "URGENT: Consider bulk discount sale or return to supplier"
            else:
                return "URGENT: Prioritize sale or mark for disposal"
        elif alert_level == ExpiryAlertLevel.HIGH:
            if quantity > 100:
                return "Implement promotional pricing or contact supplier for return"
            else:
                return "Prioritize in sales recommendations"
        elif alert_level == ExpiryAlertLevel.MEDIUM:
            return "Monitor closely and consider promotional strategies"
        elif alert_level == ExpiryAlertLevel.LOW:
            return "Plan inventory rotation and adjust reorder quantities"
        else:
            return "Monitor for future planning"
    
    async def get_expiry_alerts(
        self, 
        alert_levels: Optional[List[ExpiryAlertLevel]] = None,
        min_quantity: int = 1,
        include_expired: bool = False
    ) -> List[ExpiryAlert]:
        """Get all expiry alerts with intelligent prioritization."""
        today = date.today()
        
        # Build query conditions
        conditions = [
            InventoryBatch.is_active == True,
            InventoryBatch.current_quantity >= min_quantity,
            Product.is_active == True
        ]
        
        if not include_expired:
            conditions.append(InventoryBatch.expiry_date >= today)
        
        # Execute query
        result = await self.db.execute(
            select(InventoryBatch, Product)
            .join(Product)
            .where(and_(*conditions))
            .options(selectinload(InventoryBatch.product))
        )
        
        alerts = []
        for batch, product in result.all():
            days_until_expiry = (batch.expiry_date - today).days
            alert_level = self._calculate_alert_level(days_until_expiry)
            
            # Filter by alert levels if specified
            if alert_levels and alert_level not in alert_levels:
                continue
            
            estimated_value = float(batch.current_quantity * batch.selling_price_per_unit)
            priority_score = self._calculate_priority_score(
                days_until_expiry,
                batch.current_quantity,
                float(batch.selling_price_per_unit),
                product.is_controlled_substance
            )
            
            alert = ExpiryAlert(
                batch_id=batch.id,
                product_id=product.id,
                product_name=product.name,
                batch_number=batch.batch_number,
                current_quantity=batch.current_quantity,
                expiry_date=batch.expiry_date,
                days_until_expiry=days_until_expiry,
                alert_level=alert_level,
                estimated_value=estimated_value,
                recommended_action=self._get_recommended_action(
                    days_until_expiry, 
                    batch.current_quantity, 
                    alert_level
                ),
                priority_score=priority_score
            )
            alerts.append(alert)
        
        # Sort by priority score (highest first)
        alerts.sort(key=lambda x: x.priority_score, reverse=True)
        return alerts
    
    async def get_expiry_summary(self) -> Dict[str, any]:
        """Get summary statistics for expiry management."""
        today = date.today()
        
        # Get counts by alert level
        result = await self.db.execute(
            select(
                func.count(InventoryBatch.id).label('total_batches'),
                func.sum(InventoryBatch.current_quantity).label('total_quantity'),
                func.sum(InventoryBatch.current_quantity * InventoryBatch.selling_price_per_unit).label('total_value')
            )
            .join(Product)
            .where(
                and_(
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > 0,
                    Product.is_active == True
                )
            )
        )
        totals = result.first()
        
        # Get expiry breakdown
        expiry_breakdown = {}
        for level in ExpiryAlertLevel:
            if level == ExpiryAlertLevel.CRITICAL:
                max_days = self.settings.expiry_alert_1_week
            elif level == ExpiryAlertLevel.HIGH:
                max_days = self.settings.expiry_alert_1_month
            elif level == ExpiryAlertLevel.MEDIUM:
                max_days = self.settings.expiry_alert_3_months
            elif level == ExpiryAlertLevel.LOW:
                max_days = self.settings.expiry_alert_6_months
            else:
                continue
            
            result = await self.db.execute(
                select(
                    func.count(InventoryBatch.id).label('count'),
                    func.sum(InventoryBatch.current_quantity).label('quantity'),
                    func.sum(InventoryBatch.current_quantity * InventoryBatch.selling_price_per_unit).label('value')
                )
                .join(Product)
                .where(
                    and_(
                        InventoryBatch.is_active == True,
                        InventoryBatch.current_quantity > 0,
                        Product.is_active == True,
                        InventoryBatch.expiry_date <= today + timedelta(days=max_days),
                        InventoryBatch.expiry_date >= today
                    )
                )
            )
            breakdown = result.first()
            expiry_breakdown[level.value] = {
                'batches': breakdown.count or 0,
                'quantity': breakdown.quantity or 0,
                'value': float(breakdown.value or 0)
            }
        
        # Get expired items
        result = await self.db.execute(
            select(
                func.count(InventoryBatch.id).label('count'),
                func.sum(InventoryBatch.current_quantity).label('quantity'),
                func.sum(InventoryBatch.current_quantity * InventoryBatch.selling_price_per_unit).label('value')
            )
            .join(Product)
            .where(
                and_(
                    InventoryBatch.is_active == True,
                    InventoryBatch.current_quantity > 0,
                    Product.is_active == True,
                    InventoryBatch.expiry_date < today
                )
            )
        )
        expired = result.first()
        
        return {
            'total_batches': totals.total_batches or 0,
            'total_quantity': totals.total_quantity or 0,
            'total_value': float(totals.total_value or 0),
            'expiry_breakdown': expiry_breakdown,
            'expired': {
                'batches': expired.count or 0,
                'quantity': expired.quantity or 0,
                'value': float(expired.value or 0)
            }
        }
    
    async def mark_batch_expired(self, batch_id: int, user_id: int) -> bool:
        """Mark a batch as expired and create stock movement record."""
        from app.services.inventory_service import InventoryService
        
        batch = await self.db.execute(
            select(InventoryBatch).where(InventoryBatch.id == batch_id)
        )
        batch = batch.scalar_one_or_none()
        
        if not batch or batch.current_quantity <= 0:
            return False
        
        # Use inventory service to handle the expiry movement
        inventory_service = InventoryService(self.db)
        await inventory_service.record_stock_movement(
            product_id=batch.product_id,
            batch_id=batch_id,
            quantity=-batch.current_quantity,
            movement_type="expired",
            user_id=user_id,
            notes=f"Batch {batch.batch_number} marked as expired"
        )
        
        batch.is_expired = True
        batch.current_quantity = 0
        await self.db.commit()
        return True
