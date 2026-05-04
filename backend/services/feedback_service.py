"""Feedback Service for User Input Collection"""
from typing import Dict, Any, Optional
from backend.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.audit_service = AuditService()
    
    async def submit_query_feedback(self, query_id: int, feedback: str, 
                                     comment: str = None, client_ip: str = None) -> Dict:
        """Submit feedback for a query response"""
        
        if feedback not in ["helpful", "not_helpful"]:
            raise ValueError("Feedback must be 'helpful' or 'not_helpful'")
        
        result = self.audit_service.log_feedback(
            query_id=query_id,
            feedback=feedback,
            comment=comment,
            client_ip=client_ip
        )
        
        logger.info(f"Feedback submitted for query {query_id}: {feedback}")
        
        return {"feedback_id": result.get("feedback_id") if result else None}
    
    async def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        stats = self.audit_service.get_statistics()
        return {
            "total_feedback": stats.get("total_feedback", 0),
            "positive_feedback": stats.get("positive_feedback", 0),
            "positive_rate": (stats.get("positive_feedback", 0) / stats.get("total_feedback", 1)) * 100 if stats.get("total_feedback", 0) > 0 else 0
        }