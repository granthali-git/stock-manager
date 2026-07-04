import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'stock-manager-secret-key-12345')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'stock_manager.db')
    
    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'mock-email@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'mock-password')
    MAIL_DEFAULT_SENDER = ('Stock Manager Alert', os.environ.get('MAIL_USERNAME', 'mock-email@gmail.com'))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE_URL', '/tmp/stock_manager.db')
