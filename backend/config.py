from pydantic_settings import BaseSettings
from typing import Optional, Set
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Accounting AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: Optional[str] = None
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # LLM
    LLM_MODEL: str = "llama3.2:3b"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 500
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    CHROMA_COLLECTION_NAME: str = "accounting_docs"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".txt", ".docx"}
    UPLOAD_DIR: str = "./data/uploads"
    
    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Security
    BLOCKED_QUERY_PATTERNS: list = [
        r"delete.*data",
        r"drop.*table",
        r"rm -rf",
        r"sudo",
        r"password",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    AUDIT_LOG: bool = True
    LOG_FILE: str = "./data/logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.CHROMA_PERSIST_DIR), exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)