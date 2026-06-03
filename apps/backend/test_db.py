import sys
from pathlib import Path
from sqlalchemy import text
from app.db.session import engine

def main():
    try:
        with engine.begin() as conn:
            conn.execute(text("""
            CREATE TABLE test_table (
                id INT NOT NULL AUTO_INCREMENT,
                company_name VARCHAR(200),
                created_at TIMESTAMP NULL DEFAULT (now()),
                PRIMARY KEY (id)
            )
            """))
            print("Table created successfully")
    except Exception as e:
        print(f"Error: {repr(e)}")
        print(f"Type: {type(e)}")

if __name__ == "__main__":
    main()
