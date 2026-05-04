import ollama
from backend.config import settings
from backend.utils.logger import logger

class LLMService:
    def __init__(self):
        self.model = settings.LLM_MODEL
        self._check_ollama()
    
    def _check_ollama(self):
        try:
            ollama.list()
            logger.info(f" Ollama connected")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not running: {e}")
    
    async def generate(self, query: str, context: str) -> str:
        prompt = f"""You are an accounting assistant. Answer based ONLY on the context.

CONTEXT:
{context}

QUESTION: {query}

ANSWER (concise):"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': settings.LLM_TEMPERATURE,
                    'num_predict': settings.LLM_MAX_TOKENS
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error: {str(e)}"

llm_service = LLMService()