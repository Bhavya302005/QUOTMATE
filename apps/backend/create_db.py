import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.db.session import engine, Base
# Import all models to ensure they're registered
import app.models.user
import app.models.document
import app.models.audit_log

Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
