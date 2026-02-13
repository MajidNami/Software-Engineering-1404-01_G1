"""Database migration script to initialize schema."""
import pyodbc
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def run_migration():
    """Execute database migration scripts."""
    connection_string = (
        f"DRIVER={settings.DB_DRIVER};"
        f"SERVER={settings.DB_SERVER};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Read SQL files
        sql_dir = Path(__file__).parent.parent.parent
        
        creating_tables = sql_dir / "Creating-DataBase-Tables.sql"
        inserting_data = sql_dir / "Inserting-Data.sql"
        
        print("Running database creation script...")
        if creating_tables.exists():
            with open(creating_tables, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                # Split by GO statements
                statements = [s.strip() for s in sql_content.split('GO') if s.strip()]
                for statement in statements:
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except Exception as e:
                        print(f"Warning: {e}")
                        conn.rollback()
        
        print("Running data insertion script...")
        if inserting_data.exists():
            with open(inserting_data, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
                for statement in statements:
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except Exception as e:
                        print(f"Warning: {e}")
                        conn.rollback()
        
        cursor.close()
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
