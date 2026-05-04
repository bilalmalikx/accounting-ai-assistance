"""Minimal LLM Manager - Ollama Wrapper"""
import ollama
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.host = settings.OLLAMA_HOST
        self._check_model()
    
    def _check_model(self):
        try:
            models = ollama.list()
            model_names = [m.get('model', m.get('name', '')) for m in models.get('models', [])]
            if self.model not in model_names:
                logger.info(f"Pulling model {self.model}...")
                ollama.pull(self.model)
        except Exception as e:
            logger.error(f"Ollama error: {e}")
    
    async def generate(self, prompt: str, context: str):
        system_prompt = """You are an accounting AI assistant. Answer based ONLY on the provided context.
Be precise with numbers, dates, and amounts. If information is not in context, say 'Information not found in documents'."""
        
        user_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                options={
                    'temperature': 0.1,
                    'top_k': 40,
                    'top_p': 0.9,
                    'num_predict': 512
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"LLM failed: {e}")
            return f"Error: {str(e)}"