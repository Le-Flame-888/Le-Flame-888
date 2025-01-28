# config.py
import os
from datetime import datetime
from pathlib import Path
import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        # You can also add a file handler if you want to log to a file
        logging.FileHandler('app.log')
    ]
)

# Create logger instance
logger = logging.getLogger(__name__)

class Config:
    # Application Settings
    APP_NAME = "Hotel Management System"
    VERSION = "1.0.0"
    
    # Directory Settings
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    DATABASE_PATH = DATA_DIR / 'hotel_management.db'
    BACKUP_DIR = BASE_DIR / 'backup'
    REPORTS_DIR = BASE_DIR / 'reports'
    
    # Email Settings
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'your_hotel@example.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_password')
    
    # Business Rules
    CHECKIN_TIME = "14:00"
    CHECKOUT_TIME = "11:00"
    MAX_ADVANCE_BOOKING_DAYS = 365
    LATE_CHECKOUT_FEE = 50.0
    DEFAULT_TAX_RATE = 0.10
    
    # Currency Settings
    CURRENCY_SYMBOL = "$"
    DECIMAL_PLACES = 2
    
    # System Settings
    LOG_LEVEL = logging.INFO
    MAX_LOGIN_ATTEMPTS = 3
    SESSION_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.DATA_DIR, cls.BACKUP_DIR, cls.REPORTS_DIR]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {str(e)}")