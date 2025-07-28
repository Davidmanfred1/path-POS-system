#!/usr/bin/env python3
"""Initialize the database with sample data for Pathway Pharmacy POS System."""

import asyncio
import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import create_tables, AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.product import Product, ProductCategory
from app.models.inventory import InventoryBatch
from app.models.customer import Customer
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_sample_data():
    """Create sample data for testing the POS system."""
    
    async with AsyncSessionLocal() as db:
        try:
            # Create sample users
            print("Creating sample users...")
            
            admin_user = User(
                username="admin",
                email="admin@pharmacy.com",
                full_name="System Administrator",
                hashed_password=pwd_context.hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            
            pharmacist_user = User(
                username="pharmacist",
                email="pharmacist@pharmacy.com",
                full_name="Dr. Jane Smith",
                hashed_password=pwd_context.hash("pharma123"),
                role=UserRole.PHARMACIST,
                license_number="PH123456",
                phone="(555) 123-4567",
                is_active=True,
                is_verified=True
            )
            
            cashier_user = User(
                username="cashier",
                email="cashier@pharmacy.com",
                full_name="John Doe",
                hashed_password=pwd_context.hash("cashier123"),
                role=UserRole.CASHIER,
                phone="(555) 987-6543",
                is_active=True,
                is_verified=True
            )
            
            db.add_all([admin_user, pharmacist_user, cashier_user])
            await db.flush()
            
            # Create product categories
            print("Creating product categories...")
            
            categories = [
                ProductCategory(name="Pain Relief", description="Pain management medications"),
                ProductCategory(name="Antibiotics", description="Antibiotic medications"),
                ProductCategory(name="Vitamins", description="Vitamins and supplements"),
                ProductCategory(name="Cold & Flu", description="Cold and flu medications"),
                ProductCategory(name="Diabetes", description="Diabetes management products"),
                ProductCategory(name="Heart Health", description="Cardiovascular medications"),
                ProductCategory(name="OTC", description="Over-the-counter medications")
            ]
            
            db.add_all(categories)
            await db.flush()
            
            # Create sample products
            print("Creating sample products...")
            
            products = [
                # Pain Relief
                Product(
                    name="Ibuprofen 200mg Tablets",
                    generic_name="Ibuprofen",
                    brand_name="Advil",
                    sku="IBU200-100",
                    barcode="123456789012",
                    ndc_number="12345-678-90",
                    dosage_form="Tablet",
                    strength="200mg",
                    manufacturer="Pfizer",
                    cost_price=Decimal("22.50"),
                    selling_price=Decimal("35.99"),
                    min_stock_level=50,
                    reorder_point=25,
                    category_id=categories[0].id
                ),
                Product(
                    name="Acetaminophen 500mg Tablets",
                    generic_name="Acetaminophen",
                    brand_name="Tylenol",
                    sku="ACE500-100",
                    barcode="123456789013",
                    ndc_number="12345-678-91",
                    dosage_form="Tablet",
                    strength="500mg",
                    manufacturer="Johnson & Johnson",
                    cost_price=Decimal("17.25"),
                    selling_price=Decimal("29.99"),
                    min_stock_level=75,
                    reorder_point=30,
                    category_id=categories[0].id
                ),
                
                # Antibiotics
                Product(
                    name="Amoxicillin 500mg Capsules",
                    generic_name="Amoxicillin",
                    sku="AMX500-30",
                    ndc_number="12345-678-92",
                    dosage_form="Capsule",
                    strength="500mg",
                    manufacturer="Teva",
                    cost_price=Decimal("51.75"),
                    selling_price=Decimal("75.99"),
                    min_stock_level=30,
                    reorder_point=15,
                    requires_prescription=True,
                    category_id=categories[1].id
                ),
                Product(
                    name="Azithromycin 250mg Tablets",
                    generic_name="Azithromycin",
                    brand_name="Z-Pack",
                    sku="AZI250-6",
                    ndc_number="12345-678-93",
                    dosage_form="Tablet",
                    strength="250mg",
                    manufacturer="Pfizer",
                    cost_price=Decimal("103.50"),
                    selling_price=Decimal("143.99"),
                    min_stock_level=20,
                    reorder_point=10,
                    requires_prescription=True,
                    category_id=categories[1].id
                ),
                
                # Vitamins
                Product(
                    name="Vitamin D3 1000 IU Tablets",
                    generic_name="Cholecalciferol",
                    sku="VTD1000-100",
                    barcode="123456789014",
                    dosage_form="Tablet",
                    strength="1000 IU",
                    manufacturer="Nature Made",
                    cost_price=Decimal("36.50"),
                    selling_price=Decimal("51.99"),
                    min_stock_level=40,
                    reorder_point=20,
                    category_id=categories[2].id
                ),
                Product(
                    name="Multivitamin Adult Tablets",
                    sku="MVI-ADULT-100",
                    barcode="123456789015",
                    dosage_form="Tablet",
                    manufacturer="Centrum",
                    cost_price=Decimal("61.75"),
                    selling_price=Decimal("87.99"),
                    min_stock_level=25,
                    reorder_point=12,
                    category_id=categories[2].id
                ),
                
                # Cold & Flu
                Product(
                    name="Dextromethorphan Cough Syrup",
                    generic_name="Dextromethorphan HBr",
                    brand_name="Robitussin DM",
                    sku="DEX-SYRUP-120",
                    barcode="123456789016",
                    dosage_form="Syrup",
                    strength="15mg/5ml",
                    manufacturer="Pfizer",
                    cost_price=Decimal("27.50"),
                    selling_price=Decimal("39.99"),
                    min_stock_level=30,
                    reorder_point=15,
                    category_id=categories[3].id
                ),
                
                # Diabetes
                Product(
                    name="Metformin 500mg Tablets",
                    generic_name="Metformin HCl",
                    sku="MET500-100",
                    ndc_number="12345-678-94",
                    dosage_form="Tablet",
                    strength="500mg",
                    manufacturer="Teva",
                    cost_price=Decimal("34.50"),
                    selling_price=Decimal("51.99"),
                    min_stock_level=60,
                    reorder_point=30,
                    requires_prescription=True,
                    category_id=categories[4].id
                )
            ]
            
            db.add_all(products)
            await db.flush()
            
            # Create inventory batches with various expiry dates
            print("Creating inventory batches...")
            
            today = date.today()
            batches = []
            
            for i, product in enumerate(products):
                # Create 2-3 batches per product with different expiry dates
                batch_count = 2 if i % 2 == 0 else 3
                
                for j in range(batch_count):
                    # Vary expiry dates to test alert system
                    if j == 0:
                        # Some batches expire soon (critical alerts)
                        expiry_days = 5 + (i % 10)  # 5-14 days
                    elif j == 1:
                        # Some expire in 1-3 months (high/medium alerts)
                        expiry_days = 30 + (i % 60)  # 30-90 days
                    else:
                        # Some expire later (low/no alerts)
                        expiry_days = 180 + (i % 180)  # 180-360 days
                    
                    expiry_date = today + timedelta(days=expiry_days)
                    
                    batch = InventoryBatch(
                        product_id=product.id,
                        batch_number=f"BATCH{product.id:03d}{j+1:02d}",
                        lot_number=f"LOT{i+1:04d}{j+1}",
                        initial_quantity=100 + (i * 10),
                        current_quantity=80 + (i * 8),  # Some stock has been sold
                        cost_per_unit=product.cost_price,
                        selling_price_per_unit=product.selling_price,
                        expiry_date=expiry_date,
                        supplier_name=f"Supplier {(i % 3) + 1}",
                        purchase_order_number=f"PO{1000 + i + j}",
                        invoice_number=f"INV{2000 + i + j}"
                    )
                    batches.append(batch)
            
            db.add_all(batches)
            await db.flush()
            
            # Create sample customers
            print("Creating sample customers...")
            
            customers = [
                Customer(
                    first_name="Akosua",
                    last_name="Mensah",
                    email="akosua.mensah@gmail.com",
                    phone="+233 24 111 2222",
                    address_line1="123 Liberation Road",
                    city="Accra",
                    state="Greater Accra",
                    zip_code="GA-123-4567",
                    country="Ghana",
                    date_of_birth=date(1985, 3, 15),
                    loyalty_card_number="LC001",
                    loyalty_points=150,
                    total_spent=Decimal("1850.75")
                ),
                Customer(
                    first_name="Kwame",
                    last_name="Asante",
                    email="kwame.asante@yahoo.com",
                    phone="+233 20 333 4444",
                    address_line1="456 Osu Oxford Street",
                    city="Accra",
                    state="Greater Accra",
                    zip_code="GA-456-7890",
                    country="Ghana",
                    date_of_birth=date(1978, 7, 22),
                    loyalty_card_number="LC002",
                    loyalty_points=75,
                    total_spent=Decimal("950.50")
                ),
                Customer(
                    first_name="Ama",
                    last_name="Osei",
                    email="ama.osei@hotmail.com",
                    phone="+233 26 555 6666",
                    address_line1="789 Spintex Road",
                    city="Accra",
                    state="Greater Accra",
                    zip_code="GA-789-0123",
                    country="Ghana",
                    date_of_birth=date(1992, 11, 8),
                    loyalty_card_number="LC003",
                    loyalty_points=200,
                    total_spent=Decimal("2450.25")
                )
            ]
            
            db.add_all(customers)
            
            await db.commit()
            print("Sample data created successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating sample data: {e}")
            raise


async def main():
    """Main function to initialize database and create sample data."""
    print("Initializing Pathway Pharmacy POS System...")
    
    # Create tables
    print("Creating database tables...")
    await create_tables()
    
    # Create sample data
    await create_sample_data()
    
    print("\nDatabase initialization complete!")
    print("\nSample login credentials:")
    print("Admin: username=admin, password=admin123")
    print("Pharmacist: username=pharmacist, password=pharma123")
    print("Cashier: username=cashier, password=cashier123")


if __name__ == "__main__":
    asyncio.run(main())
