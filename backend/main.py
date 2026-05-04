from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from backend.config import settings
from backend.api.routes import health, documents, query, chat, feedback
from backend.api.middleware import auth, logging as log_middleware, rate_limit, security
from backend.utils.logger import setup_logging
from backend.utils.exceptions import (
    AccountingAIException,
    accounting_ai_exception_handler,
    GuardrailViolation,
    DocumentProcessingError
)
from backend.database.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Check Ollama connection
    try:
        import ollama
        ollama.list()
        logger.info(f"Ollama connected at {settings.OLLAMA_HOST}")
    except Exception as e:
        logger.warning(f"Ollama connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="100% Local Accounting AI Assistant with Guardrails",
    lifespan=lifespan
)

# Add exception handlers
app.add_exception_handler(AccountingAIException, accounting_ai_exception_handler)
app.add_exception_handler(GuardrailViolation, accounting_ai_exception_handler)
app.add_exception_handler(DocumentProcessingError, accounting_ai_exception_handler)

# Add middleware (order matters)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(security.SecurityHeadersMiddleware)
app.add_middleware(auth.APIKeyMiddleware)
app.add_middleware(rate_limit.RateLimitMiddleware)
app.add_middleware(log_middleware.LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "upload": "POST /api/v1/documents/upload",
            "query": "POST /api/v1/query",
            "chat": "POST /api/v1/chat"
        }
    }

@app.get("/health")
async def simple_health():
    return {"status": "alive", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.RELOAD
    )