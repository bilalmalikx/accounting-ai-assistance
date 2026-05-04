import re
from backend.utils.logger import logger

class OutputGuardrail:
    def __init__(self):
        self.sensitive_patterns = [
            r'\b\d{16}\b',
            r'\b\d{3}-\d{2}-\d{4}\b',
        ]
    
    def check(self, response: str):
        filtered = response
        
        for pattern in self.sensitive_patterns:
            if re.search(pattern, filtered):
                filtered = re.sub(pattern, "[REDACTED]", filtered)
                logger.warning("Sensitive data redacted")
        
        if len(filtered) > 2000:
            filtered = filtered[:2000] + "... [truncated]"
        
        return True, filtered