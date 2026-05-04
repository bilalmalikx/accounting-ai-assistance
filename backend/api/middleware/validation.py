from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class ValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            
            if "/upload" in request.url.path:
                if "multipart/form-data" not in content_type:
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Expected multipart/form-data"
                    )
            else:
                if "application/json" not in content_type:
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Expected application/json"
                    )
        
        return await call_next(request)