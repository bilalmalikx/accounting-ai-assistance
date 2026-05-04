from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Optional
from backend.services.query_service import QueryService
from backend.models.request_models import ChatRequest, ChatMessage
from backend.models.response_models import ChatResponse, ChatHistoryResponse
from backend.api.middleware.auth import verify_api_key
from backend.config import settings
import uuid
from datetime import datetime
import logging

router = APIRouter(dependencies=[Depends(verify_api_key)] if settings.API_KEY_ENABLED else [])
query_service = QueryService()
logger = logging.getLogger(__name__)

# In-memory session store (use Redis in production)
chat_sessions: Dict[str, list] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_req: ChatRequest):
    """Chat interface with conversation memory and guardrails"""
    
    session_id = chat_req.session_id or str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"
    
    # Get or create session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    try:
        # Process with context from history
        result = await query_service.answer_with_context(
            query=chat_req.message,
            history=chat_sessions[session_id],
            top_k=chat_req.top_k or 5,
            client_ip=client_ip,
            session_id=session_id
        )
        
        # Check if blocked
        if result.get("blocked"):
            raise HTTPException(status_code=400, detail=result.get("answer"))
        
        # Update chat history
        chat_sessions[session_id].append({
            "role": "user",
            "content": chat_req.message,
            "timestamp": datetime.now().isoformat()
        })
        chat_sessions[session_id].append({
            "role": "assistant",
            "content": result["answer"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit history size
        max_history = 50
        if len(chat_sessions[session_id]) > max_history:
            chat_sessions[session_id] = chat_sessions[session_id][-max_history:]
        
        logger.info(f"Chat session {session_id}: {len(chat_sessions[session_id])} messages")
        
        return ChatResponse(
            session_id=session_id,
            answer=result["answer"],
            sources=result.get("sources", []),
            processing_time_ms=result["processing_time_ms"],
            message_count=len(chat_sessions[session_id])
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    history = chat_sessions.get(session_id, [])
    return ChatHistoryResponse(
        session_id=session_id,
        messages=history,
        total_messages=len(history)
    )

@router.delete("/chat/{session_id}")
async def clear_chat(session_id: str):
    """Clear chat history for a session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        logger.info(f"Chat session cleared: {session_id}")
    return {"status": "cleared", "session_id": session_id}

@router.post("/chat/{session_id}/feedback")
async def submit_chat_feedback(
    session_id: str,
    message_index: int,
    feedback: str  # "helpful" or "not_helpful"
):
    """Submit feedback for a specific chat message"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if message_index >= len(chat_sessions[session_id]):
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Log feedback to audit
    from backend.services.audit_service import AuditService
    audit_service = AuditService()
    audit_service.update_chat_feedback(session_id, message_index, feedback)
    
    return {"status": "feedback_received", "message_index": message_index, "feedback": feedback}