"""Expiry management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date

from app.database import get_database
from app.services.expiry_service import ExpiryService, ExpiryAlertLevel


router = APIRouter()


class ExpiryAlertResponse(BaseModel):
    """Expiry alert response model."""
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


class ExpirySummaryResponse(BaseModel):
    """Expiry summary response model."""
    total_batches: int
    total_quantity: int
    total_value: float
    expiry_breakdown: dict
    expired: dict


@router.get("/alerts", response_model=List[ExpiryAlertResponse])
async def get_expiry_alerts(
    alert_levels: Optional[List[ExpiryAlertLevel]] = Query(None),
    min_quantity: int = Query(1, ge=0),
    include_expired: bool = Query(False),
    db: AsyncSession = Depends(get_database)
):
    """
    Get expiry alerts with intelligent prioritization.
    
    - **alert_levels**: Filter by specific alert levels (critical, high, medium, low, info)
    - **min_quantity**: Minimum quantity threshold for alerts
    - **include_expired**: Include already expired items
    """
    service = ExpiryService(db)
    
    try:
        alerts = await service.get_expiry_alerts(
            alert_levels=alert_levels,
            min_quantity=min_quantity,
            include_expired=include_expired
        )
        
        return [ExpiryAlertResponse(**alert.__dict__) for alert in alerts]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/critical", response_model=List[ExpiryAlertResponse])
async def get_critical_expiry_alerts(
    min_quantity: int = Query(1, ge=0),
    db: AsyncSession = Depends(get_database)
):
    """Get only critical expiry alerts (1 week or less)."""
    service = ExpiryService(db)
    
    try:
        alerts = await service.get_expiry_alerts(
            alert_levels=[ExpiryAlertLevel.CRITICAL],
            min_quantity=min_quantity,
            include_expired=False
        )
        
        return [ExpiryAlertResponse(**alert.__dict__) for alert in alerts]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/high-priority", response_model=List[ExpiryAlertResponse])
async def get_high_priority_expiry_alerts(
    min_quantity: int = Query(1, ge=0),
    db: AsyncSession = Depends(get_database)
):
    """Get high priority expiry alerts (critical and high levels)."""
    service = ExpiryService(db)
    
    try:
        alerts = await service.get_expiry_alerts(
            alert_levels=[ExpiryAlertLevel.CRITICAL, ExpiryAlertLevel.HIGH],
            min_quantity=min_quantity,
            include_expired=False
        )
        
        return [ExpiryAlertResponse(**alert.__dict__) for alert in alerts]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=ExpirySummaryResponse)
async def get_expiry_summary(
    db: AsyncSession = Depends(get_database)
):
    """
    Get comprehensive expiry management summary.
    
    Returns statistics about:
    - Total inventory batches and values
    - Breakdown by expiry alert levels
    - Already expired items
    """
    service = ExpiryService(db)
    
    try:
        summary = await service.get_expiry_summary()
        return ExpirySummaryResponse(**summary)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batches/{batch_id}/mark-expired")
async def mark_batch_expired(
    batch_id: int,
    user_id: int = Query(..., description="ID of user marking the batch as expired"),
    db: AsyncSession = Depends(get_database)
):
    """
    Mark a batch as expired and remove from active inventory.
    
    This will:
    - Set the batch as expired
    - Create a stock movement record for audit trail
    - Update inventory quantities
    """
    service = ExpiryService(db)
    
    try:
        success = await service.mark_batch_expired(batch_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Batch not found or already processed"
            )
        
        return {
            "message": "Batch marked as expired successfully",
            "batch_id": batch_id
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_expiry_dashboard(
    db: AsyncSession = Depends(get_database)
):
    """
    Get expiry management dashboard data.
    
    Returns a comprehensive view for pharmacy management including:
    - Summary statistics
    - Top priority alerts
    - Trends and recommendations
    """
    service = ExpiryService(db)
    
    try:
        # Get summary
        summary = await service.get_expiry_summary()
        
        # Get top 10 critical alerts
        critical_alerts = await service.get_expiry_alerts(
            alert_levels=[ExpiryAlertLevel.CRITICAL],
            min_quantity=1,
            include_expired=False
        )
        top_critical = critical_alerts[:10]
        
        # Get high-value alerts (top 10 by estimated value)
        all_alerts = await service.get_expiry_alerts(
            alert_levels=[ExpiryAlertLevel.CRITICAL, ExpiryAlertLevel.HIGH, ExpiryAlertLevel.MEDIUM],
            min_quantity=1,
            include_expired=False
        )
        high_value_alerts = sorted(all_alerts, key=lambda x: x.estimated_value, reverse=True)[:10]
        
        # Calculate total at-risk value
        total_at_risk_value = sum(alert.estimated_value for alert in all_alerts)
        
        # Generate recommendations
        recommendations = []
        
        if len(critical_alerts) > 0:
            recommendations.append({
                "type": "urgent",
                "message": f"{len(critical_alerts)} items expire within 1 week. Immediate action required.",
                "action": "Review critical alerts and implement disposal or promotional strategies."
            })
        
        high_alerts = [a for a in all_alerts if a.alert_level == ExpiryAlertLevel.HIGH]
        if len(high_alerts) > 5:
            recommendations.append({
                "type": "warning",
                "message": f"{len(high_alerts)} items expire within 1 month.",
                "action": "Consider promotional pricing or supplier return options."
            })
        
        if total_at_risk_value > 10000:
            recommendations.append({
                "type": "financial",
                "message": f"${total_at_risk_value:,.2f} in inventory at risk of expiry.",
                "action": "Review inventory management and ordering practices."
            })
        
        return {
            "summary": summary,
            "critical_alerts": [ExpiryAlertResponse(**alert.__dict__) for alert in top_critical],
            "high_value_alerts": [ExpiryAlertResponse(**alert.__dict__) for alert in high_value_alerts],
            "total_at_risk_value": total_at_risk_value,
            "recommendations": recommendations,
            "alert_counts": {
                "critical": len([a for a in all_alerts if a.alert_level == ExpiryAlertLevel.CRITICAL]),
                "high": len([a for a in all_alerts if a.alert_level == ExpiryAlertLevel.HIGH]),
                "medium": len([a for a in all_alerts if a.alert_level == ExpiryAlertLevel.MEDIUM]),
                "low": len([a for a in all_alerts if a.alert_level == ExpiryAlertLevel.LOW])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
