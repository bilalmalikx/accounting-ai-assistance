from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging
import json
from backend.utils.logger import get_logger
from backend.config import settings

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                body = body_bytes.decode()[:500]  # Limit body size
            except:
                body = "Unable to read body"
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "query_params": str(request.query_params),
                "body_preview": body
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            process_time_ms = process_time * 1000
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - {process_time_ms:.2f}ms",
                extra={
                    "status_code": response.status_code,
                    "processing_time_ms": process_time_ms,
                    "path": request.url.path
                }
            )
            
            # Add custom headers
            response.headers["X-Process-Time-MS"] = str(int(process_time_ms))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "error": str(e),
                    "path": request.url.path,
                    "processing_time_ms": process_time * 1000
                },
                exc_info=True
            )
            raise