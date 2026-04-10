#!/usr/bin/env python3
"""
Simple test to verify imports work correctly
"""

import sys
print("Testing imports...")

try:
    from app.config import settings
    print("✅ Config imported")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    sys.exit(1)

try:
    from app.database import Base, engine
    print("✅ Database imported")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    sys.exit(1)

try:
    from app.models.user import User
    print("✅ User model imported")
except Exception as e:
    print(f"❌ User model import failed: {e}")
    sys.exit(1)

try:
    from app.utils.auth import hash_password
    print("✅ Auth utils imported")
except Exception as e:
    print(f"❌ Auth utils import failed: {e}")
    sys.exit(1)

try:
    from app.routers.auth import router
    print("✅ Auth router imported")
except Exception as e:
    print(f"❌ Auth router import failed: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("✅ FastAPI app imported")
except Exception as e:
    print(f"❌ FastAPI app import failed: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")
