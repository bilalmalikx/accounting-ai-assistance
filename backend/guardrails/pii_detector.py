"""PII Detection and Redaction for Indian Financial Documents"""
import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class PIIDetector:
    def __init__(self):
        self.pii_patterns = {
            'aadhaar': r'\b[2-9]{1}[0-9]{3}[-\s]?[0-9]{4}[-\s]?[0-9]{4}\b',
            'pan': r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
            'gst': r'[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}',
            'ifsc': r'[A-Z]{4}0[A-Z0-9]{6}',
            'phone_indian': r'(?:\+91|91)?[-\s]?[6-9]\d{9}',
            'email': r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
            'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
            'bank_account': r'\b\d{9,18}\b',
            'cvv': r'\b\d{3,4}\b',
            'password': r'(?i)password\s*[=:]\s*\S+',
            'api_key': r'(?i)(api[_-]?key|token)\s*[=:]\s*[A-Za-z0-9]+',
        }
        
        self.sensitive_types = ['aadhaar', 'pan', 'credit_card', 'cvv', 'password']
    
    def detect(self, text: str) -> List[Dict[str, str]]:
        """Detect all PII in text"""
        detected = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                detected.append({
                    'type': pii_type,
                    'value': match,
                    'position': text.find(match)
                })
        
        return detected
    
    def redact(self, text: str) -> Tuple[str, List[Dict]]:
        """Redact PII from text"""
        detected = self.detect(text)
        redacted_text = text
        
        for pii in detected:
            redacted_text = redacted_text.replace(
                pii['value'],
                f"[{pii['type'].upper()}_REDACTED]"
            )
        
        if detected:
            logger.info(f"Redacted {len(detected)} PII items")
        
        return redacted_text, detected
    
    def has_sensitive_pii(self, text: str) -> bool:
        """Check for sensitive PII"""
        for pii_type in self.sensitive_types:
            if re.search(self.pii_patterns[pii_type], text):
                return True
        return False