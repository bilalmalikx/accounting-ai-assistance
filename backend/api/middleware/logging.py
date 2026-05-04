import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.utils.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        
        logger.info(f"→ {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        duration = time.time() - start
        logger.info(f"← {response.status_code} ({duration:.3f}s)")
        
        return response