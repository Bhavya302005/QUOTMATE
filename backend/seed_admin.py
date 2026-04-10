"""
Admin User Seeder Script
Creates a default admin user for testing and initial access

Usage:
    python seed_admin.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models.user import User
from app.utils.auth import hash_password
import uuid


def seed_admin():
    """Create default admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        admin_email = "admin@quotmate.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"❌ Admin user already exists: {admin_email}")
            return
        
        # Create admin user
        admin_id = str(uuid.uuid4())
        admin_user = User(
            id=admin_id,
            email=admin_email,
            password_hash=hash_password("Admin123"),  # Shorter password
            full_name="Admin User",
            company_name="QuotMate",
            phone="1234567890",
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"\n📧 Email: {admin_email}")
        print(f"🔑 Password: Admin123")
        print(f"🆔 User ID: {admin_id}")
        print(f"\n⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding admin user...")
    seed_admin()
