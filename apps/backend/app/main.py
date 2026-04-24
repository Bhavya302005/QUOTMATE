from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.session import engine, Base
from pathlib import Path
import os

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
if os.environ.get("VERCEL"):
    uploads_dir = Path("/tmp/uploads")
else:
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"

uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Database tables are normally managed by Alembic migrations
# Run: alembic upgrade head
# But since we switched to SQLite locally, we can let SQLAlchemy create them:
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Failed to initialize database tables on startup. Proceeding anyway. Error: {e}")

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
from app.api import auth, ocr, products, quotations, moms
from app.api import work_orders, dashboard, documents

# Register routers
app.include_router(auth.router)
app.include_router(ocr.router)
app.include_router(products.router)
app.include_router(quotations.router)
app.include_router(moms.router)
app.include_router(work_orders.router)
app.include_router(dashboard.router)
app.include_router(documents.router)
