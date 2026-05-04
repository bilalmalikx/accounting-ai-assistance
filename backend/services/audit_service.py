"""Complete Audit Service for Compliance and Monitoring"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.database.session import SessionLocal
from backend.models.database_models import AuditLog, QueryHistory, DocumentRecord, FeedbackRecord
from backend.config import settings

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self):
        self.db: Optional[Session] = None
    
    def _get_db(self):
        if self.db is None or not self.db.is_active:
            self.db = SessionLocal()
        return self.db
    
    def log_query(self, query: str, response: str, processing_time_ms: float, 
                  client_ip: str, status: str, model_used: str = None, 
                  sources_used: List[str] = None, risk_score: float = None,
                  guardrail_issues: List[str] = None):
        """Log query with full audit trail"""
        try:
            db = self._get_db()
            audit_log = AuditLog(
                query=query[:2000],
                response=response[:5000] if response else "",
                processing_time_ms=processing_time_ms,
                client_ip=client_ip,
                status=status,
                model_used=model_used or settings.OLLAMA_MODEL,
                sources_used=sources_used[:20] if sources_used else None,
                risk_score=risk_score,
                guardrail_issues=guardrail_issues
            )
            db.add(audit_log)
            db.commit()
            logger.debug(f"Query logged: {query[:50]}... | Status: {status}")
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            if db:
                db.rollback()
    
    def log_query_history(self, query: str, answer: str, session_id: str, 
                          user_feedback: str = None, processing_time_ms: float = None):
        """Log query for session history"""
        try:
            db = self._get_db()
            history = QueryHistory(
                query=query[:2000],
                answer=answer[:5000] if answer else "",
                session_id=session_id,
                user_feedback=user_feedback,
                processing_time_ms=processing_time_ms
            )
            db.add(history)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log history: {e}")
            if db:
                db.rollback()
    
    def log_document_upload(self, filename: str, file_hash: str, category: str, 
                           chunks_count: int, file_size: int, status: str = "success",
                           error_message: str = None):
        """Log document upload activity"""
        try:
            db = self._get_db()
            doc_record = DocumentRecord(
                filename=filename,
                file_hash=file_hash,
                category=category,
                chunks_count=chunks_count,
                file_size=file_size,
                status=status,
                error_message=error_message
            )
            db.add(doc_record)
            db.commit()
            logger.info(f"Document logged: {filename} | Status: {status}")
        except Exception as e:
            logger.error(f"Failed to log document: {e}")
            if db:
                db.rollback()
    
    def log_feedback(self, query_id: int, feedback: str, comment: str = None, client_ip: str = None):
        """Log user feedback"""
        try:
            db = self._get_db()
            feedback_record = FeedbackRecord(
                query_id=query_id,
                feedback=feedback,
                comment=comment,
                client_ip=client_ip
            )
            db.add(feedback_record)
            db.commit()
            return {"feedback_id": feedback_record.id}
        except Exception as e:
            logger.error(f"Failed to log feedback: {e}")
            if db:
                db.rollback()
            return None
    
    def update_chat_feedback(self, session_id: str, message_index: int, feedback: str):
        """Update chat message feedback"""
        try:
            db = self._get_db()
            # Find the history entry
            history = db.query(QueryHistory).filter(
                QueryHistory.session_id == session_id
            ).order_by(QueryHistory.timestamp.desc()).limit(message_index + 1).all()
            
            if history and len(history) > message_index:
                history[message_index].user_feedback = feedback
                db.commit()
        except Exception as e:
            logger.error(f"Failed to update chat feedback: {e}")
    
    def get_recent_queries(self, limit: int = 100, status_filter: str = None, hours: int = 24):
        """Get recent queries with filters"""
        db = self._get_db()
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query_obj = db.query(AuditLog).filter(AuditLog.timestamp >= cutoff)
        
        if status_filter:
            query_obj = query_obj.filter(AuditLog.status == status_filter)
        
        return query_obj.order_by(desc(AuditLog.timestamp)).limit(limit).all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit statistics"""
        db = self._get_db()
        
        total_queries = db.query(AuditLog).count()
        successful_queries = db.query(AuditLog).filter(AuditLog.status == 'success').count()
        blocked_queries = db.query(AuditLog).filter(AuditLog.status == 'blocked').count()
        filtered_queries = db.query(AuditLog).filter(AuditLog.status == 'filtered').count()
        
        avg_processing_time = db.query(func.avg(AuditLog.processing_time_ms)).filter(
            AuditLog.status == 'success'
        ).scalar() or 0
        
        # Risk statistics
        high_risk_queries = db.query(AuditLog).filter(AuditLog.risk_score >= 0.7).count()
        medium_risk_queries = db.query(AuditLog).filter(
            AuditLog.risk_score >= 0.3, AuditLog.risk_score < 0.7
        ).count()
        
        # Time-based
        last_24h = db.query(AuditLog).filter(
            AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'blocked_queries': blocked_queries,
            'filtered_queries': filtered_queries,
            'average_processing_time_ms': float(avg_processing_time),
            'high_risk_queries': high_risk_queries,
            'medium_risk_queries': medium_risk_queries,
            'queries_last_24h': last_24h,
            'unique_documents': db.query(DocumentRecord).filter(DocumentRecord.status == 'success').count(),
            'total_chunks': db.query(func.sum(DocumentRecord.chunks_count)).filter(
                DocumentRecord.status == 'success'
            ).scalar() or 0,
            'total_feedback': db.query(FeedbackRecord).count(),
            'positive_feedback': db.query(FeedbackRecord).filter(FeedbackRecord.feedback == 'helpful').count()
        }
    
    def get_query_details(self, query_id: int) -> Optional[Dict]:
        """Get detailed query information"""
        db = self._get_db()
        query_log = db.query(AuditLog).filter(AuditLog.id == query_id).first()
        
        if not query_log:
            return None
        
        return {
            "id": query_log.id,
            "timestamp": query_log.timestamp.isoformat(),
            "query": query_log.query,
            "response": query_log.response,
            "processing_time_ms": query_log.processing_time_ms,
            "client_ip": query_log.client_ip,
            "status": query_log.status,
            "risk_score": query_log.risk_score,
            "guardrail_issues": query_log.guardrail_issues,
            "sources_used": query_log.sources_used
        }
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()