from fastapi import APIRouter, Depends, HTTPException, Request
from backend.services.feedback_service import FeedbackService
from backend.models.request_models import FeedbackRequest
from backend.models.response_models import FeedbackResponse
from backend.api.middleware.auth import verify_api_key
from backend.config import settings

router = APIRouter(dependencies=[Depends(verify_api_key)] if settings.API_KEY_ENABLED else [])
feedback_service = FeedbackService()

@router.post("/feedback/query/{query_id}", response_model=FeedbackResponse)
async def submit_query_feedback(
    request: Request,
    query_id: int,
    feedback_req: FeedbackRequest
):
    """Submit feedback for a query response"""
    
    result = await feedback_service.submit_query_feedback(
        query_id=query_id,
        feedback=feedback_req.feedback,
        comment=feedback_req.comment,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    return FeedbackResponse(
        status="success",
        message="Feedback recorded",
        feedback_id=result.get("feedback_id")
    )

@router.get("/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    stats = await feedback_service.get_feedback_stats()
    return stats