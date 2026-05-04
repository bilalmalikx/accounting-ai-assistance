import re
from pathlib import Path
from backend.config import settings

def validate_filename(filename: str) -> bool:
    """Validate filename is safe"""
    dangerous_patterns = [r"\.\.", r"/", r"\\", r"%"]

    for pattern in dangerous_patterns:
        if re.search(pattern, filename):
            return False
    return True

def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS

def validate_content_type(content_type: str) -> bool:
    """Validate content type for request"""
    if "application/json" in content_type:
        return True
    if "multipart/form-data" in content_type:
        return True
    return False