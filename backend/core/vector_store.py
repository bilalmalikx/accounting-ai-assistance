import chromadb
from chromadb.utils import embedding_functions
from backend.config import settings
from backend.utils.logger import logger

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn
        )
        
        logger.info(f" ChromaDB ready: {self.collection.count()} chunks")
    
    async def add_documents(self, documents: list, metadatas: list, ids: list):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        return True
    
    async def search(self, query_embedding: list, top_k: int = None):
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return {
            "documents": results['documents'][0] if results['documents'] else [],
            "metadatas": results['metadatas'][0] if results['metadatas'] else [],
            "distances": results['distances'][0] if results['distances'] else []
        }
    
    async def get_count(self) -> int:
        return self.collection.count()

vector_store = VectorStore()