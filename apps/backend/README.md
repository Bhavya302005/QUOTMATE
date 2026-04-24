# QuotMate Backend API

Smart Business Document Generator - Backend API built with FastAPI

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL 8.0 (Railway)
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **OCR**: Google Cloud Vision API
- **AI**: NVIDIA NIMs + Llama 3.1

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Setup Railway MySQL Database

1. Go to https://railway.app
2. Create new project
3. Click "New" → "Database" → "Add MySQL"
4. Copy the DATABASE_URL from the Connect tab

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with Railway DATABASE_URL and your JWT_SECRET
```

### 5. Database Migrations

```bash
# Create a new migration (after model changes)
alembic revision --autogenerate -m "description of changes"

# Apply migrations to database
alembic upgrade head

# Check current migration version
alembic current

# Rollback one migration
alembic downgrade -1
```

### 6. Run Application

```bash
uvicorn app.main:app --reload
```

### 7. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Week 1 Deliverables

- [x] Project structure created
- [x] FastAPI app initialized
- [x] Core models created (User, Document, AuditLog)
- [x] Railway MySQL database configured
- [x] Alembic migrations setup
- [x] First migration applied

## Current API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check

More endpoints coming in Week 2+
