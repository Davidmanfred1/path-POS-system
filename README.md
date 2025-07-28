# Pathway - Pharmacy POS System

A comprehensive Point of Sale (POS) system designed specifically for pharmacies with intelligent expiry management and inventory tracking.

## Features

### Core POS Functionality
- Product catalog management
- Inventory tracking with batch numbers
- Sales transactions and receipt generation
- Customer management and loyalty programs
- Multi-user support with role-based access

### Pharmacy-Specific Features
- **Intelligent Expiry Management**: Automated alerts for products expiring in 6 months, 3 months, 1 month, and 1 week
- **Batch Tracking**: Track medications by batch numbers and expiry dates
- **Prescription Management**: Handle prescription orders and refills
- **Drug Interaction Warnings**: Basic safety checks for common interactions
- **Regulatory Compliance**: Track controlled substances and generate required reports

### Analytics & Reporting
- Sales reports (daily, weekly, monthly)
- Inventory reports with low stock alerts
- Expiry reports with upcoming expirations
- Customer purchase history
- Profit margin analysis

## Technology Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite (default, no setup required) / PostgreSQL (optional)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS with modern features)
- **Authentication**: JWT tokens
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Package Management**: uv (fast) or pip (traditional)

## Project Structure

```
pathway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and setup
│   ├── models/              # SQLAlchemy models
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── static/              # Static files (CSS, JS, images)
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Quick Start

### 🚀 One-Command Setup (Recommended)

**Linux/Mac:**
```bash
# Automatic setup with uv (fastest)
python setup.py
python run.py --init
```

**Windows:**
```cmd
# Double-click setup.bat or run in Command Prompt
setup.bat
python run.py --init
```

### Option 1: Manual Setup with uv (Fast)
```bash
# 1. Install uv (if not already installed)
pip install uv

# 2. Install dependencies with uv (much faster than pip!)
uv pip install -r requirements.txt

# 3. Initialize database and start server
python run.py --init
```

### Option 2: Manual Setup
```bash
# 1. Install uv and dependencies
pip install uv
uv pip install -r requirements.txt

# 2. Copy environment file and configure
cp .env.example .env

# 3. Initialize database with sample data
python scripts/init_sample_data.py

# 4. Start the server
python run.py
```

### Option 3: Traditional pip (Slower)
```bash
# 1. Install dependencies (traditional method)
pip install -r requirements.txt

# 2. Initialize database and start server
python run.py --init
```

> **💡 Why uv?** uv is 10-100x faster than pip for installing Python packages. It's developed by the same team behind Ruff and provides significant performance improvements for dependency management.

## Usage

### Web Interface
- **Main POS**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Expiry Dashboard**: `http://localhost:8000#expiry`

### Default Login Credentials
- **Admin**: username=`admin`, password=`admin123`
- **Pharmacist**: username=`pharmacist`, password=`pharma123`
- **Cashier**: username=`cashier`, password=`cashier123`

### Command Line Options
```bash
python run.py --help              # Show all options
python run.py --test              # Run tests
python run.py --host 0.0.0.0      # Make accessible from other machines
python run.py --port 8080         # Use different port
```

## Key Features Demonstration

### 🚨 Intelligent Expiry Alert System
The system automatically categorizes inventory by expiry risk:
- **Critical** (≤1 week): Immediate action required
- **High** (≤1 month): Promotional pricing recommended
- **Medium** (≤3 months): Monitor and plan rotation
- **Low** (≤6 months): Adjust reorder quantities

### 📊 Smart Priority Scoring
Alerts are prioritized using a sophisticated algorithm considering:
- Days until expiry (urgency)
- Inventory value at risk
- Quantity on hand
- Controlled substance status

### 💊 Pharmacy-Specific Features
- Prescription tracking and refill management
- Batch number tracking for recalls
- NDC number support
- Controlled substance monitoring
- Drug interaction warnings (basic)

### 🛒 Modern POS Interface
- Barcode scanning support
- Real-time inventory updates
- Customer loyalty program
- Multiple payment methods
- Receipt generation

## API Endpoints

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product
- `GET /api/products/search?q=query` - Search products
- `GET /api/products/barcode/{barcode}` - Find by barcode

### Expiry Management
- `GET /api/expiry/alerts` - Get all expiry alerts
- `GET /api/expiry/alerts/critical` - Critical alerts only
- `GET /api/expiry/summary` - Expiry statistics
- `GET /api/expiry/dashboard` - Complete dashboard data

## Testing

Run the comprehensive test suite:
```bash
python run.py --test
```

Tests cover:
- Expiry alert algorithm accuracy
- Priority scoring logic
- Database operations
- API endpoints
- Business logic validation

## Configuration

Key settings in `.env`:
```env
# Expiry Alert Thresholds (days)
EXPIRY_ALERT_6_MONTHS=180
EXPIRY_ALERT_3_MONTHS=90
EXPIRY_ALERT_1_MONTH=30
EXPIRY_ALERT_1_WEEK=7

# Pharmacy Information
PHARMACY_NAME=Your Pharmacy Name
PHARMACY_LICENSE=PH123456789

# Database (SQLite is default, no setup required)
DATABASE_URL=sqlite:///./pathway.db
# For PostgreSQL: postgresql://username:password@localhost/pathway_db
```

## Architecture

```
pathway/
├── app/
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── api/            # REST API endpoints
│   └── static/         # Web interface
├── scripts/            # Utility scripts
└── tests/             # Test suite
```

## Troubleshooting

### PostgreSQL Installation Issues

If you get `pg_config executable not found` error:

**Ubuntu/Debian:**
```bash
sudo apt-get install libpq-dev python3-dev
uv pip install -r requirements-postgresql.txt
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install postgresql-devel python3-devel
# or: sudo dnf install postgresql-devel python3-devel
uv pip install -r requirements-postgresql.txt
```

**macOS:**
```bash
brew install postgresql
uv pip install -r requirements-postgresql.txt
```

**Windows:**
1. Install PostgreSQL from https://www.postgresql.org/download/windows/
2. Add PostgreSQL bin directory to PATH
3. Run: `uv pip install -r requirements-postgresql.txt`

**Alternative (Pure Python, no compilation):**
```bash
uv pip install psycopg2-cffi
```

### Other Common Issues

**Python Version Error:**
- Ensure Python 3.8+ is installed: `python --version`

**Permission Errors:**
- Try: `python -m pip install --user -r requirements.txt`

**uv Not Found:**
- Install uv first: `pip install uv`

**Dependencies Fail:**
- Update pip: `python -m pip install --upgrade pip`
- Try traditional pip: `pip install -r requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details
