"""Minimal Embeddings Manager - Only initialization"""
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.model = None
        self.langchain_embeddings = None
        self._initialize()
    
    def _initialize(self):
        try:
            self.model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE
            )
            self.langchain_embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': settings.EMBEDDING_DEVICE},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"Embeddings loaded: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Embeddings failed: {e}")
            raise
    
    def get_embeddings(self):
        return self.langchain_embeddings
    
    def embed_text(self, text: str):
        return self.model.encode(text)