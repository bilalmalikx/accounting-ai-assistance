class AccountingAIException(Exception):
    """Base exception for Accounting AI"""
    pass

class DocumentNotFoundError(AccountingAIException):
    """Document not found in vector store"""
    pass

class LLMNotReadyError(AccountingAIException):
    """Ollama/LLM not ready"""
    pass

class RateLimitExceededError(AccountingAIException):
    """Rate limit exceeded"""
    pass