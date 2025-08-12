from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database connection details from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite database for testing
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'  # Use simple cache for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False    

class ProductionConfig:
    pass