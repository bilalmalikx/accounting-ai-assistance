from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pathlib import Path
import shutil
from typing import Optional
from backend.config import settings
from backend.services.document_service import DocumentService
from backend.models.request_models import DocumentUploadRequest, DocumentUploadResponse
from backend.models.response_models import DocumentValidationResponse
from backend.api.middleware.auth import verify_api_key
from backend.utils.helpers import sanitize_filename, validate_file_type
from backend.utils.exceptions import DocumentProcessingError
import logging

router = APIRouter(dependencies=[Depends(verify_api_key)] if settings.API_KEY_ENABLED else [])
document_service = DocumentService()
logger = logging.getLogger(__name__)

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    category: str = "general",
    tags: Optional[str] = None
):
    """Upload and process accounting document with validation"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Save temporarily
    temp_path = settings.TEMP_DIR / f"temp_{safe_filename}"
    file_path = settings.UPLOAD_DIR / safe_filename
    
    try:
        # Save temp file
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate file
        validation = await document_service.validate_document(temp_path)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Document validation failed: {validation['issues']}"
            )
        
        # Process document
        result = await document_service.process_document(
            file_path=temp_path,
            filename=safe_filename,
            category=category,
            tags=tags.split(",") if tags else []
        )
        
        # Move to permanent storage
        shutil.move(str(temp_path), str(file_path))
        
        logger.info(f"Document uploaded: {safe_filename}, chunks: {result['chunks_created']}")
        
        return DocumentUploadResponse(
            filename=result["filename"],
            chunks_created=result["chunks_created"],
            category=result["category"],
            file_hash=result["file_hash"],
            status="success",
            message="Document processed successfully",
            pii_redacted=result.get("pii_redacted", False),
            processing_time_ms=result.get("processing_time_ms", 0)
        )
        
    except DocumentProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Cleanup temp
        if temp_path.exists():
            temp_path.unlink()

@router.post("/documents/validate")
async def validate_document_endpoint(
    file: UploadFile = File(...)
) -> DocumentValidationResponse:
    """Validate document without processing"""
    
    temp_path = settings.TEMP_DIR / f"validate_{file.filename}"
    
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        validation = await document_service.validate_document(temp_path)
        
        return DocumentValidationResponse(
            filename=file.filename,
            is_valid=validation["is_valid"],
            issues=validation["issues"],
            file_size=validation["file_size"],
            estimated_chunks=validation.get("estimated_chunks", 0)
        )
        
    finally:
        if temp_path.exists():
            temp_path.unlink()

@router.get("/documents/list")
async def list_documents(
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all processed documents"""
    documents = await document_service.list_documents(
        category=category,
        limit=limit,
        offset=offset
    )
    return {"documents": documents, "total": len(documents)}

@router.delete("/documents/{document_hash}")
async def delete_document(document_hash: str):
    """Delete document by hash"""
    success = await document_service.delete_document(document_hash)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_hash": document_hash}