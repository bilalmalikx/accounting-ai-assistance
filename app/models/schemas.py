from pydantic import BaseModel
from typing import Optional, List

class PDFUploadResponse(BaseModel):
    message: str
    filename: str
    pages: Optional[int] = None
    chunks: Optional[int] = None

class QuestionRequest(BaseModel):
    question: str
    pdf_name: Optional[str] = None 

class AnswerResponse(BaseModel):
    question: str
    answer: str
    source_chunks: Optional[List[str]] = None
    confidence: Optional[float] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None