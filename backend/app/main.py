from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from pathlib import Path

# Import all models to ensure they're registered with Base
from app.models import User, Document, AuditLog

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Business Document Generator API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Serve uploaded files (images, generated documents)
uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Database tables are normally managed by Alembic migrations
# Run: alembic upgrade head
# But since we switched to SQLite locally, we can let SQLAlchemy create them:
Base.metadata.create_all(bind=engine)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "QuotMate API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

# Import routers
from app.routers import auth, ocr, products, quotations, moms
from app.routers import work_orders, dashboard, documents

# Register routers
app.include_router(auth.router)
app.include_router(ocr.router)
app.include_router(products.router)
app.include_router(quotations.router)
app.include_router(moms.router)
app.include_router(work_orders.router)
app.include_router(dashboard.router)
app.include_router(documents.router)
