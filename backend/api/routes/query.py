from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
from backend.services.query_service import QueryService
from backend.models.request_models import QueryRequest, BatchQueryRequest
from backend.models.response_models import QueryResponse, BatchQueryResponse
from backend.api.middleware.auth import verify_api_key
from backend.config import settings
from backend.utils.exceptions import GuardrailViolation
import logging

router = APIRouter(dependencies=[Depends(verify_api_key)] if settings.API_KEY_ENABLED else [])
query_service = QueryService()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: Request, query_req: QueryRequest):
    """Query accounting documents with full guardrails"""
    
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    try:
        # Process query with guardrails
        result = await query_service.answer_query(
            query=query_req.query,
            top_k=query_req.top_k,
            filter_category=query_req.filter_category,
            filter_tags=query_req.filter_tags,
            client_ip=client_ip,
            user_agent=user_agent,
            session_id=query_req.session_id
        )
        
        # Check if query was blocked
        if result.get("blocked"):
            raise GuardrailViolation(
                message=result.get("answer", "Query blocked by security guardrails"),
                risk_score=result.get("risk_score", 0.8)
            )
        
        # Return response
        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence_scores=result.get("scores", []),
            processing_time_ms=result["processing_time_ms"],
            filtered=result.get("filtered", False),
            extracted_amounts=result.get("extracted_amounts", []),
            warning=result.get("warning")
        )
        
    except GuardrailViolation as e:
        logger.warning(f"Query blocked: {query_req.query[:50]}... Risk: {e.risk_score}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.post("/query/batch", response_model=BatchQueryResponse)
async def batch_query(request: Request, batch_req: BatchQueryRequest):
    """Process multiple queries in batch"""
    
    client_ip = request.client.host if request.client else "unknown"
    results = []
    
    for query_req in batch_req.queries[:10]:  # Limit to 10 queries per batch
        try:
            result = await query_service.answer_query(
                query=query_req.query,
                top_k=query_req.top_k,
                filter_category=query_req.filter_category,
                client_ip=client_ip
            )
            results.append({
                "query": query_req.query,
                "success": not result.get("blocked", False),
                "answer": result.get("answer", ""),
                "processing_time_ms": result.get("processing_time_ms", 0)
            })
        except Exception as e:
            results.append({
                "query": query_req.query,
                "success": False,
                "error": str(e)
            })
    
    return BatchQueryResponse(results=results, total_queries=len(results))

@router.post("/query/extract")
async def extract_financial_data(request: Request, query_req: QueryRequest):
    """Extract specific financial data with structured output"""
    
    client_ip = request.client.host if request.client else "unknown"
    
    result = await query_service.extract_financial_data(
        query=query_req.query,
        client_ip=client_ip
    )
    
    return result