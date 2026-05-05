from app.components.vector_store import VectorStoreComponent
from typing import List, Dict, Any
from app.utils.config import config

class RetrievalService:
    def __init__(self):
        self.vector_store = VectorStoreComponent()
        self.top_k = config.TOP_K_RESULTS
    
    def retrieve_relevant_chunks(self, question: str, pdf_name: str = None) -> List[Dict[str, Any]]:
        """
        Question ke relevant chunks dhundta hai
        Agar pdf_name specified hai to sirf us PDF se dhundhega
        """
        # Load vector store agar load nahi hai
        if self.vector_store.vector_store is None:
            self.vector_store.load_vector_store()
        
        # Similarity search
        results = self.vector_store.similarity_search(question, k=self.top_k)
        
        # Format results with metadata
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": None  # Chroma score nahi deta, FAISS use karoge to milega
            })
        
        # Filter by pdf_name if specified
        if pdf_name:
            filtered = [r for r in formatted_results if r["metadata"].get("pdf_name") == pdf_name]
            if filtered:
                return filtered
            else:
                # Agar specified PDF mein kuch nahi mila, to warning ke saath empty return
                return []
        
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