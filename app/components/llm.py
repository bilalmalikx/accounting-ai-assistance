import ollama
from typing import List, Dict, Any
from app.utils.config import config

class LLMComponent:
    def __init__(self):
        self.model = config.LLM_MODEL
        self.base_url = config.OLLAMA_BASE_URL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
        
        # Verify Ollama is running and model is available
        self._check_model_availability()
    
    def _check_model_availability(self):
        """Check if Ollama is running and model is installed"""
        try:
            # List available models
            models = ollama.list()
            model_names = [m['model'] for m in models.get('models', [])]
            
            if self.model not in model_names:
                print(f"⚠️ Warning: Model '{self.model}' not found in Ollama")
                print(f"Available models: {model_names}")
                print(f"Run: ollama pull {self.model}")
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {e}")
            print("Make sure Ollama is running: ollama serve")
    
    def generate_response(self, prompt: str) -> str:
        """Generate simple response from prompt"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_with_context(self, question: str, context: str) -> str:
        """Generate response using context (RAG)"""
        system_prompt = """You are a helpful accounting assistant. Using the provided document context, answer the user's question.

GUIDELINES:
- If the question asks for "first step" or "steps", look for numbered items, bullet points, or sequential information.
- If exact answer not found, provide the MOST RELEVANT information you CAN find.
- If the context has related concepts, explain them.
- ONLY say "I don't know" if the context is completely empty.
- Be specific with numbers, dates, and amounts from the context.

Be helpful and extract value from whatever context is provided."""
        
        user_prompt = f"""Context:
{context}

Question: {question}

Answer based only on the above context:"""
        
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
            
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"Error: {str(e)}. Make sure Ollama is running with 'ollama serve'"
    
    def get_llm_instance(self):
        """Return self for compatibility"""
        return self