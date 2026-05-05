from fastapi import APIRouter, HTTPException
from app.services.qa_service import QAService
from app.services.guardrails_service import GuardrailsService
from app.models.schemas import QuestionRequest, AnswerResponse, ErrorResponse

router = APIRouter()
qa_service = QAService()
guardrails_service = GuardrailsService()

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Angular se question receive karta hai
    Answer generate karta hai aur return karta hai
    """
    try:
        # Validate question
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Generate answer using QA service
        result = qa_service.answer_question(
            question=request.question,
            pdf_name=request.pdf_name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["answer"])
        
        # Apply guardrails validation
        is_valid, validated_answer = guardrails_service.validate_answer(
            result["answer"],
            " ".join([s["content"] for s in result["sources"]])
        )
        
        if not is_valid:
            validated_answer = "I cannot provide an accurate answer based on the document content."
        
        # Sanitize final answer
        final_answer = guardrails_service.sanitize_answer(validated_answer)
        
        return AnswerResponse(
            question=request.question,
            answer=final_answer,
            source_chunks=[s["content"] for s in result["sources"][:2]] if result["sources"] else [],
            confidence=result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ErrorResponse(
            error="Question processing failed",
            details=str(e)
        )

@router.get("/health")
async def ask_health():
    """Check if QA service is working"""
    return {"status": "qa_service_ok"}