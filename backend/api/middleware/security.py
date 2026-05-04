from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import re
from backend.utils.security_utils import sanitize_input, detect_sql_injection
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class RequestSanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Sanitize query parameters
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                sanitized_params[key] = sanitize_input(value)
            
            # Modify request scope (limited capability)
            request.scope["query_string"] = str(sanitized_params).encode()
        
        # Check for SQL injection in query params
        for key, value in request.query_params.items():
            if detect_sql_injection(value):
                logger.warning(f"SQL injection attempt detected in {key}: {value}")
                return Response("Invalid request", status_code=400)
        
        return await call_next(request)