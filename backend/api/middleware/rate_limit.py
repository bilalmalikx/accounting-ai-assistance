from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
import time
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
    
    async def dispatch(self, request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for health and docs
        skip_paths = ["/api/v1/health", "/health", "/docs", "/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < settings.RATE_LIMIT_PERIOD
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_PERIOD} seconds",
                    "retry_after": settings.RATE_LIMIT_PERIOD
                }
            )
        
        self.requests[client_ip].append(now)
        return await call_next(request)