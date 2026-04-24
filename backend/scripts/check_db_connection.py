#!/usr/bin/env python3
"""Smoke-check MySQL connectivity and list tables (not run by pytest)."""
import sys
from pathlib import Path

# Project root: backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import engine
from app.models import Base

try:
    with engine.connect() as connection:
        print("✅ Database connection successful!")

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully (create_all).")

    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")

except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
