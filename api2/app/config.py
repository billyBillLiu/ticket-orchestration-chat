from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "Ticket Orchestration Chat API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "localhost"
    port: int = 3080            # localhost:3080
    
    # CORS settings
    allowed_origins: List[str] = [
        "http://localhost:3000",  # React dev server (Create React App)
        "http://localhost:3090",  # Your Vite dev server (actual port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3090",
    ]
    
    # Database settings
    database_url: Optional[str] = None
    
    # JWT settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days (7 * 24 * 60)
    
    # File upload settings
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env file

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True) 