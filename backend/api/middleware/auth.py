from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import settings
from backend.utils.logger import logger

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public paths
        public_paths = ["/health", "/", "/docs", "/redoc", "/openapi.json"]
        
        if request.url.path in public_paths:
            return await call_next(request)
        
        if settings.API_KEY:
            api_key = request.headers.get("X-API-Key")
            
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="X-API-Key header required"
                )
            
            if api_key != settings.API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid API key"
                )
        
        return await call_next(request)