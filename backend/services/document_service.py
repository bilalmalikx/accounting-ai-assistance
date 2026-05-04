import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import settings
from backend.core.vector_store import vector_store
from backend.utils.helpers import generate_document_id, generate_chunk_id
from backend.utils.logger import logger

class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
    
    async def process_document(self, file: UploadFile):
        # Save file
        file_path = Path(settings.UPLOAD_DIR) / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Load PDF
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()
        
        # Split
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        doc_id = generate_document_id(file.filename)
        
        for i, chunk in enumerate(chunks):
            chunk_id = generate_chunk_id(doc_id, i)
            await vector_store.add_documents(
                documents=[chunk.page_content],
                metadatas=[{
                    "source": file.filename,
                    "page": chunk.metadata.get("page", 0),
                    "doc_id": doc_id
                }],
                ids=[chunk_id]
            )
        
        logger.info(f"Processed {file.filename}: {len(chunks)} chunks")
        
        return {
            "chunks": len(chunks),
            "total": await vector_store.get_count()
        }

document_service = DocumentService()