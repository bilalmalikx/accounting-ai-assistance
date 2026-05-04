"""SQLAlchemy Database Models for Audit and Storage"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_status', 'status'),
        Index('idx_audit_client_ip', 'client_ip'),
    )
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text)
    processing_time_ms = Column(Float)
    client_ip = Column(String(45))
    status = Column(String(20), default='success')  # success, blocked, filtered, error
    model_used = Column(String(50))
    sources_used = Column(JSON)
    risk_score = Column(Float)
    guardrail_issues = Column(JSON)

class QueryHistory(Base):
    __tablename__ = 'query_history'
    __table_args__ = (
        Index('idx_history_session', 'session_id'),
        Index('idx_history_timestamp', 'timestamp'),
    )
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text)
    session_id = Column(String(100))
    user_feedback = Column(String(10))  # helpful, not_helpful
    processing_time_ms = Column(Float)

class DocumentRecord(Base):
    __tablename__ = 'documents'
    __table_args__ = (
        Index('idx_doc_hash', 'file_hash'),
        Index('idx_doc_category', 'category'),
        Index('idx_doc_uploaded', 'uploaded_at'),
    )
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    category = Column(String(50), default='general')
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    chunks_count = Column(Integer, default=0)
    file_size = Column(Integer)
    status = Column(String(20), default='success')
    error_message = Column(Text, nullable=True)
    tags = Column(JSON, default=list)

class FeedbackRecord(Base):
    __tablename__ = 'feedback_records'
    __table_args__ = (
        Index('idx_feedback_query', 'query_id'),
        Index('idx_feedback_timestamp', 'timestamp'),
    )
    
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, nullable=False)
    feedback = Column(String(20), nullable=False)  # helpful, not_helpful
    comment = Column(Text, nullable=True)
    client_ip = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

class SecurityEvent(Base):
    __tablename__ = 'security_events'
    __table_args__ = (
        Index('idx_security_timestamp', 'timestamp'),
        Index('idx_security_type', 'event_type'),
    )
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(String(50), nullable=False)  # injection_attempt, pii_detected, rate_limit
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    client_ip = Column(String(45))
    details = Column(JSON)
    query_preview = Column(String(200))