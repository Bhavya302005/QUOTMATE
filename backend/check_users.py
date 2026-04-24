import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"[{u.email}] [hash length={len(u.password_hash)}] [admin={u.is_admin}] [hash={u.password_hash[:10]}...]")
    
# Let's test the provided password
from app.utils.auth import verify_password
matches = [verify_password("1234567a", u.password_hash) for u in users]
print(f"Does '1234567a' match any? {matches}")
