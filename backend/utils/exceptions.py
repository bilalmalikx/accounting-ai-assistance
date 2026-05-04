"""Custom Exceptions for Accounting AI Assistant"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AccountingAIException(Exception):
    """Base exception for Accounting AI Assistant"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class GuardrailViolation(AccountingAIException):
    """Guardrail security violations"""
    def __init__(self, message: str, risk_score: float = 0.0):
        self.risk_score = risk_score
        super().__init__(message, "GUARDRAIL_VIOLATION", 400)

class DocumentProcessingError(AccountingAIException):
    """Document processing related errors"""
    def __init__(self, message: str):
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR", 422)

class VectorStoreError(AccountingAIException):
    """Vector store related errors"""
    def __init__(self, message: str):
        super().__init__(message, "VECTOR_STORE_ERROR", 500)

class LLMError(AccountingAIException):
    """LLM related errors"""
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR", 503)

class RateLimitExceeded(AccountingAIException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)

async def accounting_ai_exception_handler(request: Request, exc: AccountingAIException):
    """Global exception handler"""
    logger.error(f"Exception: {exc.error_code} - {exc.message}")
    
    content = {
        "error": exc.error_code,
        "message": exc.message,
        "status_code": exc.status_code
    }
    
    if hasattr(exc, 'risk_score'):
        content["risk_score"] = exc.risk_score
    
    if hasattr(exc, 'retry_after'):
        content["retry_after"] = exc.retry_after
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )