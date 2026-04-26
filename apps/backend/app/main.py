from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.session import engine, Base
from pathlib import Path
import os
import logging
from time import perf_counter
from urllib.parse import urlparse

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quotmate.api")


def _database_runtime_summary(database_url: str) -> str:
    """Build a sanitized DB summary for startup diagnostics."""
    parsed = urlparse(database_url)
    scheme = parsed.scheme or "unknown"

    if scheme.startswith("sqlite"):
        sqlite_target = parsed.path or ":memory:"
        return f"dialect=sqlite target={sqlite_target} persistent={'no' if sqlite_target in (':memory:', '/:memory:') else 'yes'}"

    host = parsed.hostname or "unknown"
    database = parsed.path.lstrip("/") if parsed.path else "unknown"
    return f"dialect={scheme} host={host} database={database} persistent=yes"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_origin_regex="https://.*",
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


@app.on_event("startup")
async def log_startup_event() -> None:
    logger.info("startup event: QuotMate API is starting")
    logger.info("runtime auth_config token_expiry_hours=%s", settings.ACCESS_TOKEN_EXPIRE_HOURS)
    logger.info("runtime db_config %s", _database_runtime_summary(settings.DATABASE_URL))


@app.on_event("shutdown")
async def log_shutdown_event() -> None:
    logger.info("shutdown event: QuotMate API is stopping")


@app.middleware("http")
async def log_request_duration(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start_time) * 1000
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

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
