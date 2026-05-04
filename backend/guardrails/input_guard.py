import re
from backend.config import settings
from backend.utils.logger import logger

class InputGuardrail:
    def __init__(self):
        self.blocked_patterns = settings.BLOCKED_QUERY_PATTERNS
    
    def check(self, query: str):
        for pattern in self.blocked_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Blocked: {pattern}")
                return False, f"Query contains blocked pattern"
        
        if len(query) > 500:
            return False, "Query too long (max 500 chars)"
        
        if len(query) < 3:
            return False, "Query too short"
        
        return True, "OK"
    
    def sanitize(self, query: str) -> str:
        query = re.sub(r'\s+', ' ', query)
        return query.strip()