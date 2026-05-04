from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health and docs endpoints
        skip_paths = ["/api/v1/health", "/", "/docs", "/openapi.json", "/health", "/redoc"]
        
        if request.url.path in skip_paths or request.url.path.startswith("/docs"):
            return await call_next(request)
        
        if settings.API_KEY_ENABLED:
            api_key = request.headers.get("X-API-Key")
            
            if not api_key:
                logger.warning(f"Missing API key for {request.url.path}")
                raise HTTPException(
                    status_code=401,
                    detail="API key is required",
                    headers={"WWW-Authenticate": "API-Key"}
                )
            
            if api_key != settings.API_KEY:
                logger.warning(f"Invalid API key for {request.url.path}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "API-Key"}
                )
        
        return await call_next(request)

async def verify_api_key(request: Request):
    """Dependency for route-level API key verification"""
    if not settings.API_KEY_ENABLED:
        return True
    
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True