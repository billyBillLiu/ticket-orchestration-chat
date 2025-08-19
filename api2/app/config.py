from pydantic_settings import BaseSettings
from typing import Optional, List, Dict
import os
from .constants import (
    PROVIDERS, 
    MODELS,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    ACTIVE_PROVIDER,
    ACTIVE_MODEL
)

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
    
    # LLM Settings - Centralized Configuration
    llm_provider: str = ACTIVE_PROVIDER  # Default to first provider
    llm_model: str = ACTIVE_MODEL  # Default to first model of first provider
    available_providers: List[str] = PROVIDERS
    available_models: Dict[str, List[str]] = MODELS
    
    # Provider-specific settings
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434"
    openai_base_url: str = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    openai_api_key: Optional[str] = None
    
    # LLM Generation settings
    default_temperature: float = DEFAULT_TEMPERATURE
    default_max_tokens: int = DEFAULT_MAX_TOKENS

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