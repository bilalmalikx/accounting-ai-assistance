from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.routes import health, documents, query, chat
from backend.api.middleware import AuthMiddleware, RateLimitMiddleware, LoggingMiddleware
from backend.utils.logger import setup_logger, logger

# Setup logging
setup_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (only if API_KEY is set)
if settings.API_KEY:
    app.add_middleware(AuthMiddleware)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(query.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 LLM: {settings.LLM_MODEL}")

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }