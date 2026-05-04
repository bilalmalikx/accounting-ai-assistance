"""Request Models for API Endpoints"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class QueryRequest(BaseModel):
    query: str = Field(..., description="Accounting query", min_length=2, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    filter_category: Optional[str] = Field(None, description="Filter by document category")
    filter_tags: Optional[List[str]] = Field(None, description="Filter by tags")
    session_id: Optional[str] = Field(None, description="Session ID for conversation")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class BatchQueryRequest(BaseModel):
    queries: List[QueryRequest] = Field(..., max_items=10, description="List of queries")
    
    @validator('queries')
    def validate_batch(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 queries per batch')
        return v

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class DocumentUploadRequest(BaseModel):
    category: str = Field(default="general", description="Document category")
    tags: Optional[List[str]] = Field(default=[], description="Document tags")

class FeedbackRequest(BaseModel):
    feedback: str = Field(..., description="Feedback: helpful or not_helpful")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment")
    
    @validator('feedback')
    def validate_feedback(cls, v):
        if v not in ['helpful', 'not_helpful']:
            raise ValueError('Feedback must be helpful or not_helpful')
        return v

class DocumentUploadResponse(BaseModel):
    filename: str
    chunks_created: int
    category: str
    file_hash: str
    status: str
    message: str
    pii_redacted: bool = False
    processing_time_ms: float = 0

class DocumentValidationResponse(BaseModel):
    filename: str
    is_valid: bool
    issues: List[str]
    file_size: int
    estimated_chunks: int