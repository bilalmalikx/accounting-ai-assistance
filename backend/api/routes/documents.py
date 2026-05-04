from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pathlib import Path
from backend.config import settings
from backend.services.document_service import document_service
from backend.services.audit_service import audit_service
from backend.utils.logger import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """Upload and process document"""
    
    # Validate
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension {ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    try:
        result = await document_service.process_document(file)
        
        await audit_service.log_document_upload(
            filename=file.filename,
            chunks=result["chunks"],
            user_ip=request.client.host,
            status="success"
        )
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": result["chunks"],
            "total_chunks": result["total"]
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))