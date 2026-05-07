from app.components.vector_store import VectorStoreComponent
from typing import List, Dict, Any
from app.utils.config import config

class RetrievalService:
    def __init__(self):
        self.vector_store = VectorStoreComponent()
        self.top_k = config.TOP_K_RESULTS
    
    def retrieve_relevant_chunks(self, question: str, pdf_name: str = None, pdf_names: List[str] = None) -> List[Dict[str, Any]]:
        """
        Question ke relevant chunks dhundta hai
        - pdf_name: single PDF ke liye
        - pdf_names: multiple PDFs ke liye
        """
        # Load vector store agar load nahi hai
        if self.vector_store.vector_store is None:
            self.vector_store.load_vector_store()
        
        all_results = []
        
        # ✅ MULTIPLE PDFs CASE
        if pdf_names and len(pdf_names) > 0:
            for name in pdf_names:
                results = self.vector_store.similarity_search(question, pdf_name=name, k=self.top_k)
                all_results.extend(results)
            
            # Remove duplicates by content
            seen = set()
            unique_results = []
            for doc in all_results:
                if doc.page_content not in seen:
                    seen.add(doc.page_content)
                    unique_results.append(doc)
            results = unique_results[:self.top_k]
        
        # ✅ SINGLE PDF CASE
        elif pdf_name:
            results = self.vector_store.similarity_search(question, pdf_name=pdf_name, k=self.top_k)
        
        # ✅ NO FILTER (search all PDFs)
        else:
            results = self.vector_store.similarity_search(question, k=self.top_k)
        
        # Format results with metadata
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": None
            })
        
        return formatted_results
    
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Multiple chunks ko ek single context string mein convert karta hai"""
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"].get("pdf_name", "unknown")
            context_parts.append(f"[Source: {source}]\n{chunk['content']}\n")
        
        return "\n---\n".join(context_parts)
    
    def get_chunks_with_page_numbers(self, question: str) -> List[Dict[str, Any]]:
        """Page numbers ke saath chunks return karta hai (citation ke liye)"""
        results = self.retrieve_relevant_chunks(question)
        
        for result in results:
            page = result["metadata"].get("page", 0)
            result["page_number"] = page + 1 if isinstance(page, int) else 0
        
        return results