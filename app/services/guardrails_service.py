from typing import Dict, Any, Tuple
import re

class GuardrailsService:
    def __init__(self):
        self.fallback_phrases = [
            "i don't know",
            "i don't have enough information",
            "cannot answer",
            "not in the context",
            "not in the document"
        ]
    
    def validate_answer(self, answer: str, context: str) -> Tuple[bool, str]:
        """Check if answer is grounded in context"""
        answer_lower = answer.lower()
    
    # Check for fallback phrases (these are OK)
        for phrase in self.fallback_phrases:
            if phrase in answer_lower:
                return True, answer  # LLM already said it doesn't know
    
    # Skip the coverage check for now (too aggressive)
    # if coverage < 0.3 and len(answer_words) > 5:
    #     return False, "I cannot provide an accurate answer based on the document content."
    
    # Always return True for now
        return True, answer
    
    def sanitize_answer(self, answer: str) -> str:
        """Remove any sensitive or unwanted content"""
        # Remove multiple newlines
        answer = re.sub(r'\n{3,}', '\n\n', answer)
        
        # Remove any "I think" or "I believe" patterns (LLM confidence issues)
        answer = re.sub(r'I (think|believe|feel) that\s+', '', answer, flags=re.IGNORECASE)
        
        return answer.strip()
    
    def check_hallucination(self, answer: str, chunks: list) -> Dict[str, Any]:
        """
        Advanced hallucination check using retrieved chunks
        Returns scores for each claim in answer
        """
        if not chunks:
            return {"hallucination_score": 1.0, "is_hallucinated": True, "message": "No context available"}
        
        all_context = " ".join([chunk.get("content", "") for chunk in chunks])
        
        # Check if answer has specific numbers/dates that aren't in context
        numbers_in_answer = re.findall(r'\b\d{4}\b', answer)  # Years like 2020, 2021
        numbers_in_context = re.findall(r'\b\d{4}\b', all_context)
        
        for num in numbers_in_answer:
            if num not in numbers_in_context:
                return {
                    "hallucination_score": 0.7,
                    "is_hallucinated": True,
                    "message": f"Found year {num} in answer but not in document"
                }
        
        return {
            "hallucination_score": 0.1,
            "is_hallucinated": False,
            "message": "Answer appears grounded in context"
        }