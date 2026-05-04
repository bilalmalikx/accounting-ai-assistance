from fastapi import APIRouter, Depends
from typing import Dict, Any
import ollama
import psutil
import time
from backend.config import settings
from backend.core.embeddings import EmbeddingsManager
from backend.core.vector_store import VectorStoreManager
from backend.api.middleware.auth import verify_api_key

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check"""
    status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {},
        "system": {}
    }
    
    # Check Ollama
    try:
        ollama_list = ollama.list()
        status["components"]["ollama"] = {
            "status": "up",
            "model": settings.OLLAMA_MODEL,
            "models_available": len(ollama_list.get("models", []))
        }
    except Exception as e:
        status["components"]["ollama"] = {"status": "down", "error": str(e)}
        status["status"] = "degraded"
    
    # Check Embeddings
    try:
        emb_manager = EmbeddingsManager()
        status["components"]["embeddings"] = {
            "status": "up",
            "model": settings.EMBEDDING_MODEL,
            "device": settings.EMBEDDING_DEVICE
        }
    except Exception as e:
        status["components"]["embeddings"] = {"status": "down", "error": str(e)}
        status["status"] = "degraded"
    
    # Check Vector Store
    try:
        vs_manager = VectorStoreManager()
        count = vs_manager.get_document_count()
        status["components"]["vector_store"] = {
            "status": "up",
            "document_count": count,
            "collection": settings.CHROMA_COLLECTION_NAME
        }
    except Exception as e:
        status["components"]["vector_store"] = {"status": "down", "error": str(e)}
        status["status"] = "degraded"
    
    # System metrics
    status["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent
    }
    
    return status

@router.get("/health/ready")
async def readiness_check() -> Dict[str, str]:
    """Kubernetes readiness probe"""
    try:
        ollama.list()
        return {"status": "ready"}
    except:
        return {"status": "not_ready"}

@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Kubernetes liveness probe"""
    return {"status": "alive"}