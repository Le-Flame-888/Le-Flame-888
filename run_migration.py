from database.connection import DatabaseConnection
from database.migration import migrate_guests_table

if __name__ == "__main__":
    db = DatabaseConnection('hotel_management.db')  # or whatever your database file is named
    try:
        migrate_guests_table(db)
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {str(e)}")
    finally:
        db.close()