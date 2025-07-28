"""Product management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from decimal import Decimal

from app.database import get_database
from app.services.product_service import ProductService
from app.services.expiry_service import ExpiryService


router = APIRouter()


# Pydantic models for request/response
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    generic_name: Optional[str] = Field(None, max_length=200)
    brand_name: Optional[str] = Field(None, max_length=200)
    barcode: Optional[str] = Field(None, max_length=50)
    sku: str = Field(..., min_length=1, max_length=50)
    ndc_number: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    dosage_form: Optional[str] = Field(None, max_length=50)
    strength: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    cost_price: Decimal = Field(..., ge=0)
    selling_price: Decimal = Field(..., ge=0)
    markup_percentage: Optional[Decimal] = Field(None, ge=0, le=1000)
    min_stock_level: int = Field(10, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: int = Field(5, ge=0)
    requires_prescription: bool = False
    is_controlled_substance: bool = False
    controlled_substance_schedule: Optional[str] = Field(None, max_length=10)
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    generic_name: Optional[str] = Field(None, max_length=200)
    brand_name: Optional[str] = Field(None, max_length=200)
    barcode: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    dosage_form: Optional[str] = Field(None, max_length=50)
    strength: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    markup_percentage: Optional[Decimal] = Field(None, ge=0, le=1000)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    requires_prescription: Optional[bool] = None
    is_controlled_substance: Optional[bool] = None
    controlled_substance_schedule: Optional[str] = Field(None, max_length=10)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    generic_name: Optional[str]
    brand_name: Optional[str]
    barcode: Optional[str]
    sku: str
    ndc_number: Optional[str]
    description: Optional[str]
    dosage_form: Optional[str]
    strength: Optional[str]
    manufacturer: Optional[str]
    cost_price: Decimal
    selling_price: Decimal
    markup_percentage: Optional[Decimal]
    min_stock_level: int
    max_stock_level: Optional[int]
    reorder_point: int
    requires_prescription: bool
    is_controlled_substance: bool
    controlled_substance_schedule: Optional[str]
    category_id: Optional[int]
    is_active: bool
    is_discontinued: bool
    
    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new product."""
    service = ProductService(db)
    
    # Check if SKU already exists
    existing = await service.get_product_by_sku(product.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Check if barcode already exists (if provided)
    if product.barcode:
        existing = await service.get_product_by_barcode(product.barcode)
        if existing:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    try:
        new_product = await service.create_product(product.model_dump())
        return ProductResponse.model_validate(new_product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_database)
):
    """Get all products with pagination."""
    service = ProductService(db)
    products = await service.get_all_products(
        category_id=category_id,
        active_only=active_only,
        skip=skip,
        limit=limit
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=1),
    category_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_database)
):
    """Search products by name, generic name, brand name, or SKU."""
    service = ProductService(db)
    products = await service.search_products(
        query=q,
        category_id=category_id,
        active_only=active_only,
        limit=limit
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get product by ID."""
    service = ProductService(db)
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    db: AsyncSession = Depends(get_database)
):
    """Get product by SKU."""
    service = ProductService(db)
    product = await service.get_product_by_sku(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.get("/barcode/{barcode}", response_model=ProductResponse)
async def get_product_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(get_database)
):
    """Get product by barcode."""
    service = ProductService(db)
    product = await service.get_product_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update product."""
    service = ProductService(db)
    
    # Remove None values from update data
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    
    updated_product = await service.update_product(product_id, update_data)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse.model_validate(updated_product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Soft delete product (mark as inactive)."""
    service = ProductService(db)
    success = await service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.get("/{product_id}/expiry-alerts")
async def get_product_expiry_alerts(
    product_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get expiry alerts for a specific product."""
    # Verify product exists
    product_service = ProductService(db)
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    expiry_service = ExpiryService(db)
    alerts = await expiry_service.get_expiry_alerts()
    
    # Filter alerts for this product
    product_alerts = [alert for alert in alerts if alert.product_id == product_id]
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "alerts": product_alerts
    }


# Category endpoints
@router.post("/categories/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new product category."""
    service = ProductService(db)
    try:
        new_category = await service.create_category(category.model_dump())
        return CategoryResponse.model_validate(new_category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_database)
):
    """Get all product categories."""
    service = ProductService(db)
    categories = await service.get_all_categories(active_only=active_only)
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get category by ID."""
    service = ProductService(db)
    category = await service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)
