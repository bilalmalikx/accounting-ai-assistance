from fastapi import APIRouter
import ollama
import chromadb
from backend.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "services": {},
        "system": {}
    }
    
    # Check Ollama
    try:
        ollama.list()
        status["services"]["ollama"] = "connected"
    except Exception as e:
        status["services"]["ollama"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # Check ChromaDB
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        status["services"]["chromadb"] = "connected"
    except Exception as e:
        status["services"]["chromadb"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # System info
    import shutil
    total, used, free = shutil.disk_usage(".")
    status["system"]["disk_free_gb"] = free // (2**30)
    status["system"]["disk_total_gb"] = total // (2**30)
    
    return status