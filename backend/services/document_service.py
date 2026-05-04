"""Complete Document Processing Service with Validation"""
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import hashlib
import logging
import time
from typing import Dict, List, Optional
from backend.core.vector_store import VectorStoreManager
from backend.guardrails.pii_detector import PIIDetector
from backend.guardrails.input_guard import InputGuard
from backend.utils.helpers import calculate_file_hash, sanitize_filename, truncate_text, validate_file_type
from backend.services.audit_service import AuditService
from backend.config import settings

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.pii_detector = PIIDetector()
        self.input_guard = InputGuard()
        self.audit_service = AuditService()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    async def process_document(self, file_path: Path, filename: str, category: str = "general", tags: List[str] = None) -> Dict:
        """Process uploaded document with full guardrails"""
        start_time = time.time()
        
        # 1. Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        # 2. Validate document
        validation = await self.validate_document(file_path)
        if not validation['is_valid']:
            self.audit_service.log_document_upload(
                filename=safe_filename,
                file_hash="",
                category=category,
                chunks_count=0,
                file_size=file_path.stat().st_size,
                status="failed",
                error_message=", ".join(validation['issues'])
            )
            raise ValueError(f"Document validation failed: {validation['issues']}")
        
        # 3. Calculate file hash
        file_hash = calculate_file_hash(file_path)
        
        # 4. Load document
        try:
            if file_path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            documents = loader.load()
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise ValueError(f"Cannot load document: {str(e)}")
        
        # 5. Scan and redact PII
        all_text = " ".join([doc.page_content for doc in documents])
        pii_detected = self.pii_detector.detect(all_text)
        pii_redacted = False
        
        if self.pii_detector.has_sensitive_pii(all_text):
            logger.warning(f"Sensitive PII found in {filename}")
            for doc in documents:
                doc.page_content, _ = self.pii_detector.redact(doc.page_content)
            pii_redacted = True
        
        # 6. Add metadata
        for doc in documents:
            doc.metadata["source"] = safe_filename
            doc.metadata["category"] = category
            doc.metadata["file_hash"] = file_hash
            doc.metadata["document_type"] = "accounting"
            doc.metadata["tags"] = tags or []
            doc.metadata["processed_at"] = time.time()
        
        # 7. Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # 8. Add to vector store
        chunks_count = self.vector_store.add_documents(chunks, {
            "source": safe_filename,
            "category": category,
            "file_hash": file_hash,
            "tags": tags or []
        })
        
        # 9. Log to audit
        processing_time_ms = (time.time() - start_time) * 1000
        self.audit_service.log_document_upload(
            filename=safe_filename,
            file_hash=file_hash,
            category=category,
            chunks_count=chunks_count,
            file_size=file_path.stat().st_size,
            status="success"
        )
        
        logger.info(f"Processed {filename}: {chunks_count} chunks, {len(pii_detected)} PII items, {processing_time_ms:.0f}ms")
        
        return {
            "filename": safe_filename,
            "chunks_created": chunks_count,
            "category": category,
            "file_hash": file_hash,
            "pii_redacted": pii_redacted,
            "pii_count": len(pii_detected),
            "processing_time_ms": processing_time_ms
        }
    
    async def validate_document(self, file_path: Path) -> Dict:
        """Validate document before processing"""
        issues = []
        
        if not file_path.exists():
            issues.append("File does not exist")
        
        file_size = file_path.stat().st_size
        if file_size > settings.MAX_UPLOAD_SIZE:
            issues.append(f"File too large: {file_size} bytes (max: {settings.MAX_UPLOAD_SIZE})")
        
        if file_size == 0:
            issues.append("File is empty")
        
        # Estimate chunks
        estimated_chunks = int(file_size / 500)  # Rough estimate
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "file_size": file_size,
            "estimated_chunks": estimated_chunks
        }
    
    async def list_documents(self, category: str = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """List processed documents from audit"""
        # Get statistics from audit
        stats = self.audit_service.get_statistics()
        return []  # Would need separate tracking
    
    async def delete_document(self, document_hash: str) -> bool:
        """Delete document from vector store"""
        return self.vector_store.delete_document(document_hash)