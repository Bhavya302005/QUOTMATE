import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect
from app.db.session import engine

def main():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("ℹ️  The database is connected, but there are NO tables inside.")
        else:
            print("✅ Connection successful! Current tables in database:")
            for table in tables:
                print(f"  • {table}")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    main()
