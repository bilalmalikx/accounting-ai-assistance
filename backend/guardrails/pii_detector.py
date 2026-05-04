import re

class PIIDetector:
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b[6-9]\d{9}\b',
            'aadhar': r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b',
        }
    
    def has_pii(self, text: str) -> bool:
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        return False
    
    def mask(self, text: str) -> str:
        for pattern in self.patterns.values():
            text = re.sub(pattern, "[REDACTED]", text)
        return text