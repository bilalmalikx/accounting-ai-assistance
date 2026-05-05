from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import upload, ask
from app.components.vector_store import VectorStoreComponent
from app.utils.config import config
from app.middleware import (
    log_requests_middleware,
    validation_exception_handler,
    http_exception_handler,
    api_error_handler,
    APIError
)

import os

app = FastAPI(
    title="PDF QA System with LangGraph",
    description="Ask questions from your PDF documents using AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8080", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests_middleware)


app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(APIError, api_error_handler)


app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(ask.router, prefix="/api", tags=["Ask"])


@app.on_event("startup")
async def startup_event():
    """Server start hota hai to ye chalega"""
    print("=" * 50)
    print(" Starting PDF QA System with LangGraph")
    print("=" * 50)
    
    # Ensure directories exist
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # For logging
    
    # Load existing vector store
    vector_store = VectorStoreComponent()
    vector_store.load_vector_store()
    
    if vector_store.vector_store:
        print(" Loaded existing vector store")
    else:
        print(" No existing vector store found. Upload a PDF to get started.")
    
    print(f"📖 API docs: http://localhost:8000/docs")
    print(f"🔗 Angular should connect to: http://localhost:8000")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Server band hota hai to ye chalega"""
    print("👋 Shutting down PDF QA System...")


@app.get("/")
async def root():
    return {
        "message": "PDF QA System API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/upload",
            "ask": "POST /api/ask",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    from app.middleware.logging import request_logger
    return {
        "status": "healthy",
        "service": "pdf-qa-backend",
        "stats": request_logger.get_stats()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )