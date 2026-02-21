from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChatWithRepo"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_DB_PATH: str = "data/chroma"
    DATA_PATH: str = "data"
    
    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "embeddinggemma:latest"
    CHAT_MODEL: str = "gpt-oss:20b"
    
    # Security
    SECRET_KEY: str = "chat-with-repo-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
os.makedirs(settings.DATA_PATH, exist_ok=True)
os.makedirs("logs", exist_ok=True)
