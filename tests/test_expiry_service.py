"""Tests for the expiry service and alert algorithm."""

import pytest
import asyncio
from datetime import date, timedelta
from decimal import Decimal

from app.database import AsyncSessionLocal, create_tables, drop_tables
from app.models.product import Product, ProductCategory
from app.models.inventory import InventoryBatch
from app.services.expiry_service import ExpiryService, ExpiryAlertLevel


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database."""
    await create_tables()
    yield
    await drop_tables()


@pytest.fixture
async def db_session(setup_database):
    """Create a database session for testing."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def sample_data(db_session):
    """Create sample data for testing."""
    # Create category
    category = ProductCategory(name="Test Category", description="Test category")
    db_session.add(category)
    await db_session.flush()
    
    # Create product
    product = Product(
        name="Test Medicine",
        sku="TEST001",
        cost_price=Decimal("10.00"),
        selling_price=Decimal("15.00"),
        category_id=category.id
    )
    db_session.add(product)
    await db_session.flush()
    
    # Create batches with different expiry dates
    today = date.today()
    batches = [
        # Critical: expires in 3 days
        InventoryBatch(
            product_id=product.id,
            batch_number="CRITICAL001",
            initial_quantity=50,
            current_quantity=30,
            cost_per_unit=Decimal("10.00"),
            selling_price_per_unit=Decimal("15.00"),
            expiry_date=today + timedelta(days=3)
        ),
        # High: expires in 20 days
        InventoryBatch(
            product_id=product.id,
            batch_number="HIGH001",
            initial_quantity=100,
            current_quantity=75,
            cost_per_unit=Decimal("10.00"),
            selling_price_per_unit=Decimal("15.00"),
            expiry_date=today + timedelta(days=20)
        ),
        # Medium: expires in 60 days
        InventoryBatch(
            product_id=product.id,
            batch_number="MEDIUM001",
            initial_quantity=200,
            current_quantity=150,
            cost_per_unit=Decimal("10.00"),
            selling_price_per_unit=Decimal("15.00"),
            expiry_date=today + timedelta(days=60)
        ),
        # Low: expires in 120 days
        InventoryBatch(
            product_id=product.id,
            batch_number="LOW001",
            initial_quantity=300,
            current_quantity=250,
            cost_per_unit=Decimal("10.00"),
            selling_price_per_unit=Decimal("15.00"),
            expiry_date=today + timedelta(days=120)
        ),
        # Info: expires in 300 days
        InventoryBatch(
            product_id=product.id,
            batch_number="INFO001",
            initial_quantity=400,
            current_quantity=350,
            cost_per_unit=Decimal("10.00"),
            selling_price_per_unit=Decimal("15.00"),
            expiry_date=today + timedelta(days=300)
        )
    ]
    
    db_session.add_all(batches)
    await db_session.commit()
    
    return {
        'product': product,
        'category': category,
        'batches': batches
    }


class TestExpiryService:
    """Test cases for the expiry service."""
    
    async def test_get_expiry_alerts(self, db_session, sample_data):
        """Test getting expiry alerts."""
        service = ExpiryService(db_session)
        alerts = await service.get_expiry_alerts()
        
        # Should have 5 alerts (one for each batch)
        assert len(alerts) == 5
        
        # Check alert levels are correctly assigned
        alert_levels = [alert.alert_level for alert in alerts]
        assert ExpiryAlertLevel.CRITICAL in alert_levels
        assert ExpiryAlertLevel.HIGH in alert_levels
        assert ExpiryAlertLevel.MEDIUM in alert_levels
        assert ExpiryAlertLevel.LOW in alert_levels
        assert ExpiryAlertLevel.INFO in alert_levels
    
    async def test_critical_alerts_only(self, db_session, sample_data):
        """Test filtering for critical alerts only."""
        service = ExpiryService(db_session)
        alerts = await service.get_expiry_alerts(
            alert_levels=[ExpiryAlertLevel.CRITICAL]
        )
        
        # Should have 1 critical alert
        assert len(alerts) == 1
        assert alerts[0].alert_level == ExpiryAlertLevel.CRITICAL
        assert alerts[0].batch_number == "CRITICAL001"
    
    async def test_priority_scoring(self, db_session, sample_data):
        """Test that alerts are properly prioritized."""
        service = ExpiryService(db_session)
        alerts = await service.get_expiry_alerts()
        
        # Alerts should be sorted by priority score (highest first)
        for i in range(len(alerts) - 1):
            assert alerts[i].priority_score >= alerts[i + 1].priority_score
        
        # Critical alert should have highest priority
        critical_alert = next(a for a in alerts if a.alert_level == ExpiryAlertLevel.CRITICAL)
        assert critical_alert.priority_score == max(alert.priority_score for alert in alerts)
    
    async def test_expiry_summary(self, db_session, sample_data):
        """Test expiry summary statistics."""
        service = ExpiryService(db_session)
        summary = await service.get_expiry_summary()
        
        # Check summary structure
        assert 'total_batches' in summary
        assert 'total_quantity' in summary
        assert 'total_value' in summary
        assert 'expiry_breakdown' in summary
        assert 'expired' in summary
        
        # Should have 5 total batches
        assert summary['total_batches'] == 5
        
        # Check expiry breakdown has all levels
        breakdown = summary['expiry_breakdown']
        assert 'critical' in breakdown
        assert 'high' in breakdown
        assert 'medium' in breakdown
        assert 'low' in breakdown
    
    async def test_recommended_actions(self, db_session, sample_data):
        """Test that appropriate actions are recommended."""
        service = ExpiryService(db_session)
        alerts = await service.get_expiry_alerts()
        
        # Find critical alert
        critical_alert = next(a for a in alerts if a.alert_level == ExpiryAlertLevel.CRITICAL)
        assert "URGENT" in critical_alert.recommended_action
        
        # Find high alert
        high_alert = next(a for a in alerts if a.alert_level == ExpiryAlertLevel.HIGH)
        assert len(high_alert.recommended_action) > 0
    
    async def test_mark_batch_expired(self, db_session, sample_data):
        """Test marking a batch as expired."""
        service = ExpiryService(db_session)
        
        # Get the critical batch
        critical_batch = sample_data['batches'][0]
        original_quantity = critical_batch.current_quantity
        
        # Mark as expired
        success = await service.mark_batch_expired(critical_batch.id, user_id=1)
        assert success
        
        # Refresh the batch
        await db_session.refresh(critical_batch)
        
        # Check that batch is marked as expired and quantity is zero
        assert critical_batch.is_expired
        assert critical_batch.current_quantity == 0
    
    async def test_minimum_quantity_filter(self, db_session, sample_data):
        """Test filtering alerts by minimum quantity."""
        service = ExpiryService(db_session)
        
        # Get alerts with minimum quantity of 100
        alerts = await service.get_expiry_alerts(min_quantity=100)
        
        # Should exclude batches with less than 100 items
        for alert in alerts:
            assert alert.current_quantity >= 100
    
    async def test_estimated_value_calculation(self, db_session, sample_data):
        """Test that estimated values are calculated correctly."""
        service = ExpiryService(db_session)
        alerts = await service.get_expiry_alerts()
        
        for alert in alerts:
            # Find corresponding batch
            batch = next(b for b in sample_data['batches'] 
                        if b.batch_number == alert.batch_number)
            
            expected_value = float(batch.current_quantity * batch.selling_price_per_unit)
            assert abs(alert.estimated_value - expected_value) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
