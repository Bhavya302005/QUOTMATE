from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
import pymysql
import threading
import time

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()


def _mysql_connect_args(url: str) -> dict:
    """Enable TLS for managed MySQL hosts; config strips ?ssl-mode= from DATABASE_URL."""
    if not url:
        return {}
    lowered = url.lower()
    if any(h in lowered for h in ("aivencloud.com", "railway.app", "psdb.cloud")):
        return {"ssl": {}}
    return {}


# Create engine with optimized pooling for remote DB (Railway)
# - pool_size=5: keep 5 connections warm (avoids 1.3s connect per request)
# - max_overflow=10: allow burst up to 15 total connections
# - pool_recycle=1800: recycle connections every 30min (Railway may drop idle)
# - pool_pre_ping=True: verify connection is alive before use
# - echo=False: don't log SQL — saves significant I/O overhead
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    engine_args = {
        "connect_args": {"check_same_thread": False},
        "echo": False
    }
else:
    engine_args = {
        "connect_args": _mysql_connect_args(db_url),
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 1800,
        "pool_timeout": 15,
        "echo": False,
    }

engine = create_engine(db_url, **engine_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models (modern SQLAlchemy 2.0+ pattern)
class Base(DeclarativeBase):
    pass

# Warm up the connection pool in background (don't block server startup)
def _warm_pool():
    """Pre-create a DB connection so first request doesn't wait 1.3s."""
    try:
        start = time.time()
        conn = engine.connect()
        conn.close()
        elapsed = (time.time() - start) * 1000
        print(f"✅ DB pool warmed in {elapsed:.0f}ms")
    except Exception as e:
        print(f"⚠️  DB pool warm-up failed (will retry on first request): {e}")

threading.Thread(target=_warm_pool, daemon=True).start()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
