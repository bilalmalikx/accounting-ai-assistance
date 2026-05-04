import hashlib
import uuid
from datetime import datetime

def generate_document_id(filename: str) -> str:
    """Generate unique document ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}_{filename}"

def generate_chunk_id(doc_id: str, chunk_index: int) -> str:
    """Generate unique chunk ID"""
    return f"{doc_id}_chunk_{chunk_index}"

def hash_text(text: str) -> str:
    """Create hash of text for deduplication"""
    return hashlib.md5(text.encode()).hexdigest()

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."