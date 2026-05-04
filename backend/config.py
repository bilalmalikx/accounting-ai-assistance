from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import json

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Accounting AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-in-production"
    ENVIRONMENT: str = "production"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 2
    RELOAD: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:4200", "http://localhost:3000"]
    
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_TIMEOUT: int = 120
    
    # Vector Store
    CHROMA_PERSIST_DIR: Path = Path("./data/chromadb")
    CHROMA_COLLECTION_NAME: str = "accounting_docs"
    CHROMA_DISTANCE_METHOD: str = "cosine"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".csv", ".xlsx"]
    UPLOAD_DIR: Path = Path("./data/uploads")
    TEMP_DIR: Path = Path("./data/temp")
    
    # Security
    API_KEY_ENABLED: bool = False
    API_KEY: str = ""
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    MAX_REQUESTS_PER_IP_PER_MINUTE: int = 60
    
    # Guardrails
    ENABLE_INPUT_GUARD: bool = True
    ENABLE_OUTPUT_GUARD: bool = True
    ENABLE_PII_DETECTION: bool = True
    ENABLE_PROMPT_INJECTION_DETECTION: bool = True
    ENABLE_ACCOUNTING_RULES: bool = True
    INPUT_GUARD_THRESHOLD: float = 0.6
    OUTPUT_GUARD_THRESHOLD: float = 0.7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("./data/logs/app.log")
    LOG_FORMAT: str = "json"
    AUDIT_DB_PATH: Path = Path("./data/audit.db")
    AUDIT_ENABLED: bool = True
    
    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    RETRIEVAL_STRATEGY: str = "mmr"
    
    # Performance
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    
    # Monitoring
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

settings = Settings()