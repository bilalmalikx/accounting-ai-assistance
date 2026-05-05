from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.ingestion_service import IngestionService
from app.models.schemas import PDFUploadResponse, ErrorResponse
import os
import shutil
from app.utils.config import config
import uuid

router = APIRouter()
ingestion_service = IngestionService()

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Angular se PDF file receive karta hai
    Process karta hai aur vector store mein save karta hai
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Create unique filename to avoid conflicts
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(config.UPLOAD_DIR, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF (ingestion)
        result = ingestion_service.process_pdf(file_path, file.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Clean up temp file after processing
        os.remove(file_path)
        
        return PDFUploadResponse(
            message=result["message"],
            filename=file.filename,
            pages=result.get("pages"),
            chunks=result.get("chunks")
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Processing failed",
                details=str(e)
            ).dict()
        )

@router.get("/health")
async def upload_health():
    """Check if upload service is working"""
    return {"status": "upload_service_ok"}