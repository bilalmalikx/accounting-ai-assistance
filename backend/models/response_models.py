"""Response Models for API Endpoints"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SourceDocument(BaseModel):
    content: str
    source: str
    category: str
    relevance_score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    confidence_scores: List[float]
    processing_time_ms: float
    filtered: bool = False
    extracted_amounts: Optional[List[float]] = None
    warning: Optional[str] = None

class BatchQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_queries: int

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[SourceDocument]
    processing_time_ms: float
    message_count: int = 0

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    total_messages: int

class FeedbackResponse(BaseModel):
    status: str
    message: str
    feedback_id: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    components: Dict[str, Any]
    system: Dict[str, Any]

class AuditStatsResponse(BaseModel):
    total_queries: int
    successful_queries: int
    blocked_queries: int
    filtered_queries: int
    average_processing_time_ms: float
    high_risk_queries: int
    medium_risk_queries: int
    queries_last_24h: int
    unique_documents: int
    total_chunks: int
    total_feedback: int
    positive_feedback: int