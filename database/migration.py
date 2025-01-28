# database/migration.py
from database.config import logger

def migrate_guests_table(db_connection):
    """
    Migrates the guests table to split the name field into first_name and last_name.
    """
    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create new table with desired schema
            cursor.execute("""
            CREATE TABLE guests_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Copy existing data, splitting the name field
            cursor.execute("""
            INSERT INTO guests_new (id, first_name, last_name, email, phone, address, created_at)
            SELECT 
                id,
                CASE 
                    WHEN instr(name, ' ') > 0 
                    THEN substr(name, 1, instr(name, ' ') - 1)
                    ELSE name
                END as first_name,
                CASE 
                    WHEN instr(name, ' ') > 0 
                    THEN substr(name, instr(name, ' ') + 1)
                    ELSE ''
                END as last_name,
                email, phone, address, created_at
            FROM guests
            """)
            
            # Drop old table
            cursor.execute("DROP TABLE guests")
            
            # Rename new table
            cursor.execute("ALTER TABLE guests_new RENAME TO guests")
            
            # Create indexes if needed
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_guest_names ON guests(first_name, last_name)")
            
            conn.commit()
            logger.info("Successfully migrated guests table to split name field")
            
    except Exception as e:
        logger.error(f"Failed to migrate guests table: {str(e)}")
        raise

def rollback_migration(db_connection):
    """
    Rollback function in case migration fails
    """
    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create backup of original table if it exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests_backup AS 
            SELECT id, 
                   first_name || ' ' || last_name as name,
                   email, phone, address, created_at 
            FROM guests
            """)
            
            # Drop current table
            cursor.execute("DROP TABLE IF EXISTS guests")
            
            # Create original table structure
            cursor.execute("""
            CREATE TABLE guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Restore data
            cursor.execute("""
            INSERT INTO guests 
            SELECT * FROM guests_backup
            """)
            
            # Clean up backup
            cursor.execute("DROP TABLE guests_backup")
            
            conn.commit()
            logger.info("Successfully rolled back guests table migration")
            
    except Exception as e:
        logger.error(f"Failed to rollback migration: {str(e)}")
        raise