"""Security Utilities for Input Sanitization"""
import re
import html
from typing import List

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # HTML escape
    text = html.escape(text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    if len(text) > 2000:
        text = text[:2000] + "... [truncated]"
    
    return text

def detect_sql_injection(text: str) -> bool:
    """Detect SQL injection patterns"""
    sql_patterns = [
        r'(\bSELECT\b.*\bFROM\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bOR\b.*=.*--)',
        r'(\bAND\b.*=.*--)',
        r"('.*--)|(;.*--)",
    ]
    
    text_upper = text.upper()
    for pattern in sql_patterns:
        if re.search(pattern, text_upper):
            return True
    return False

def sanitize_filename_secure(filename: str) -> str:
    """Securely sanitize filename"""
    # Remove path traversal
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')
    
    # Only alphanumeric, dot, underscore, hyphen
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Ensure not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename[:255]

def mask_sensitive_data(text: str) -> str:
    """Mask sensitive data in logs"""
    # Mask emails
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', text)
    
    # Mask IP addresses
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', text)
    
    return text