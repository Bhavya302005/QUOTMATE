#!/usr/bin/env python3
"""Test database connection"""
import sys
sys.path.insert(0, '/Users/dhrumilamin/Desktop/QuotMate/backend')

from app.database import engine
from app.models import Base

try:
    # Test connection
    with engine.connect() as connection:
        print("✅ Database connection successful!")
        
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
