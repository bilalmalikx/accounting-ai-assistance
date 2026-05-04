from backend.core.embeddings import embedding_service
from backend.core.vector_store import vector_store
from backend.core.llm import llm_service
from backend.guardrails.input_guard import InputGuardrail
from backend.guardrails.output_guard import OutputGuardrail
from backend.services.audit_service import audit_service
from backend.utils.logger import logger

class RAGPipeline:
    def __init__(self):
        self.input_guard = InputGuardrail()
        self.output_guard = OutputGuardrail()
    
    async def process_query(self, query: str, user_ip: str = "unknown"):
        import time
        start = time.time()
        
        # Input guard
        is_safe, msg = self.input_guard.check(query)
        if not is_safe:
            return {
                "answer": msg,
                "sources": [],
                "status": "blocked",
                "total_chunks": await vector_store.get_count()
            }
        
        # Search
        query_embedding = await embedding_service.get_embedding(query)
        search_results = await vector_store.search(query_embedding)
        
        if not search_results["documents"]:
            return {
                "answer": "No relevant documents found.",
                "sources": [],
                "status": "no_results",
                "total_chunks": await vector_store.get_count()
            }
        
        # Generate
        context = "\n\n---\n\n".join(search_results["documents"])
        answer = await llm_service.generate(query, context)
        
        # Output guard
        _, filtered_answer = self.output_guard.check(answer)
        
        # Audit
        await audit_service.log_query(
            query=query,
            response=filtered_answer,
            sources=search_results["metadatas"],
            duration=time.time() - start,
            user_ip=user_ip
        )
        
        return {
            "answer": filtered_answer,
            "sources": [s.get('source', 'unknown') for s in search_results["metadatas"]],
            "status": "success",
            "total_chunks": await vector_store.get_count()
        }

rag_pipeline = RAGPipeline()