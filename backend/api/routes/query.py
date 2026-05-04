from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.core.rag_pipeline import rag_pipeline
from backend.utils.logger import logger

router = APIRouter(prefix="/query", tags=["Query"])

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    status: str
    total_chunks: int = 0

@router.post("/", response_model=QueryResponse)
async def query_documents(request: Request, query_req: QueryRequest):
    """Ask a question about uploaded documents"""
    
    logger.info(f"Query: {query_req.query[:100]}...")
    
    try:
        result = await rag_pipeline.process_query(
            query=query_req.query,
            user_ip=request.client.host
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            status=result["status"],
            total_chunks=result.get("total_chunks", 0)
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))