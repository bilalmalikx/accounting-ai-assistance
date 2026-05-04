from sentence_transformers import SentenceTransformer
from backend.config import settings
from backend.utils.logger import logger

class EmbeddingService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f" Embedding model loaded: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    async def get_embedding(self, text: str) -> list:
        if not self.model:
            self._load_model()
        return self.model.encode(text).tolist()
    
    async def get_embeddings_batch(self, texts: list) -> list:
        if not self.model:
            self._load_model()
        return self.model.encode(texts).tolist()

embedding_service = EmbeddingService()