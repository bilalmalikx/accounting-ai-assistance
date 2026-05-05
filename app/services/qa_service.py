from app.services.retrieval_service import RetrievalService
from app.components.llm import LLMComponent
from typing import Dict, Any, Optional

class QAService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_component = LLMComponent()
    
    def answer_question(self, question: str, pdf_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete QA pipeline:
        1. Retrieve relevant chunks
        2. Format context
        3. Generate answer using LLM
        4. Return answer with sources
        """
        try:
            # Step 1: Retrieve chunks
            chunks = self.retrieval_service.retrieve_relevant_chunks(question, pdf_name)
            
            if not chunks:
                return {
                    "success": True,
                    "answer": "No relevant information found in the document(s).",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Step 2: Format context
            context = self.retrieval_service.format_context(chunks)
            
            # Step 3: Generate answer
            answer = self.llm_component.generate_with_context(question, context)
            
            # Step 4: Extract sources for citation
            sources = []
            for chunk in chunks[:2]:  # Sirf top 2 sources
                source_info = {
                    "content": chunk["content"][:200] + "...",  # Preview
                    "pdf_name": chunk["metadata"].get("pdf_name", "unknown"),
                    "page": chunk["metadata"].get("page", 0)
                }
                sources.append(source_info)
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "confidence": 0.8 if chunks else 0.0
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def answer_with_citations(self, question: str) -> Dict[str, Any]:
        """Citations (page numbers) ke saath answer return karta hai"""
        result = self.answer_question(question)
        
        if result["success"] and result["sources"]:
            # Answer mein citations add karna optional
            citations = [f"(Source: {s['pdf_name']}, Page {s['page']})" for s in result["sources"]]
            result["citations"] = citations
        
        return result