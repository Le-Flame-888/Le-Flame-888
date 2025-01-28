# database/connection.py
import sqlite3
from datetime import datetime
from database.config import logger

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.initialize_database()

    def get_connection(self):
        """Get or create database connection"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def initialize_database(self):
        """Initialize the database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create Rooms table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_number TEXT PRIMARY KEY,
                    room_type TEXT NOT NULL,
                    rate REAL NOT NULL,
                    status TEXT DEFAULT 'Available',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # Create Guests table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # Create Reservations table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guest_id INTEGER,
                    room_number TEXT,
                    check_in_date DATE NOT NULL,
                    check_out_date DATE NOT NULL,
                    status TEXT DEFAULT 'Confirmed',
                    total_amount REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guest_id) REFERENCES guests (id),
                    FOREIGN KEY (room_number) REFERENCES rooms (room_number)
                )
                """)

                # Create Payments table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reservation_id INTEGER,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_method TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reservation_id) REFERENCES reservations (id)
                )             
                """)

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None