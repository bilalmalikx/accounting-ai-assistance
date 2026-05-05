"""Minimal Vector Store Manager"""
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.core.embeddings import EmbeddingsManager
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.embeddings = EmbeddingsManager()
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        self._initialize()
    
    def _initialize(self):
        try:
            self.vector_store = Chroma(
                persist_directory=str(settings.CHROMA_PERSIST_DIR),
                embedding_function=self.embeddings.get_embeddings(),
                collection_name=settings.CHROMA_COLLECTION_NAME
            )
            logger.info("Vector store initialized")
        except Exception as e:
            logger.error(f"Vector store failed: {e}")
            raise
    
    def add_documents(self, documents, metadata=None):
        chunks = self.text_splitter.split_documents(documents)
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)
        
        self.vector_store.add_documents(chunks)
        self.vector_store.persist()
        return len(chunks)
    
    def search(self, query: str, k: int = 5, filter_dict=None):
        results = self.vector_store.similarity_search_with_score(query, k=k, filter=filter_dict)
        filtered = [(doc, score) for doc, score in results if score >= settings.SIMILARITY_THRESHOLD]
        return filtered
    
    def get_document_count(self):
        try:
            return self.vector_store._collection.count()
        except:
            return 0
    
    def delete_document(self, doc_id: str):
        try:
            self.vector_store.delete([doc_id])
            return True
        except:
            return False