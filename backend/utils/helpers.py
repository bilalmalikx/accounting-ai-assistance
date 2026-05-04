"""Helper Functions for Common Operations"""
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    pattern = r'\d+(?:\.\d+)?'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches if match]

def parse_date_from_text(text: str) -> Optional[datetime]:
    """Extract date from text"""
    date_patterns = [
        (r'(\d{4})-(\d{2})-(\d{2})', 'ymd'),
        (r'(\d{2})/(\d{2})/(\d{4})', 'dmy'),
        (r'(\d{2})-(\d{2})-(\d{4})', 'dmy'),
        (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', 'mdY'),
    ]
    
    for pattern, format_type in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                if format_type == 'ymd':
                    return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                elif format_type == 'dmy':
                    return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
                elif format_type == 'mdY':
                    month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                                 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                    month = month_map[match.group(2).lower()]
                    return datetime(int(match.group(3)), month, int(match.group(1)))
            except:
                continue
    return None

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing unsafe characters"""
    unsafe_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(unsafe_chars, '_', filename)
    return sanitized[:255]

def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions

def format_currency(amount: float, currency: str = "₹") -> str:
    """Format amount as currency"""
    return f"{currency} {amount:,.2f}"

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def json_serializer(obj: Any) -> str:
    """Custom JSON serializer for objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)

def load_json_file(file_path: Path) -> Dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load JSON: {e}")

def save_json_file(data: Dict, file_path: Path) -> None:
    """Save data to JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=json_serializer)