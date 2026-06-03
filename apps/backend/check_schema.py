import asyncio
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_schema():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print(f"Checking database URL: {settings.DATABASE_URL}")
        # For MySQL
        try:
            result = conn.execute(text("DESCRIBE users;"))
            for row in result:
                if row[0] == 'company_logo_url':
                    print("MySQL 'users' table - company_logo_url schema:")
                    print(row)
        except Exception as e:
            pass
            
        # For PostgreSQL
        try:
            result = conn.execute(text("SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = 'users';"))
            for row in result:
                if row[0] == 'company_logo_url':
                    print("PostgreSQL 'users' table - company_logo_url schema:")
                    print(row)
        except Exception as e:
            pass

if __name__ == "__main__":
    check_schema()
