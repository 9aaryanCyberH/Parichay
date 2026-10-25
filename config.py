import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    """Application configuration for Parichay."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "parichay-career-intelligence-dev-key-2026")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    UPLOAD_EXTENSIONS = [".pdf"]
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    
    # AI API Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Server configuration
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
