import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import settings
from backend.utils.logger import logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < settings.RATE_LIMIT_PERIOD
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_PERIOD}s"
            )
        
        self.requests[client_ip].append(now)
        return await call_next(request)