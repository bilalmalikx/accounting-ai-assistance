from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.core.rag_pipeline import rag_pipeline

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@router.post("/")
async def chat(request: Request, chat_req: ChatRequest):
    """Chat interface"""
    
    result = await rag_pipeline.process_query(
        query=chat_req.message,
        user_ip=request.client.host
    )
    
    return {
        "response": result["answer"],
        "sources": result["sources"],
        "session_id": chat_req.session_id or "new_session"
    }