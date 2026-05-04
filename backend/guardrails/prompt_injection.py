"""Prompt Injection Detection and Prevention"""
import re
from typing import Tuple, List

class PromptInjectionDetector:
    def __init__(self):
        self.injection_patterns = [
            (r"(?i)ignore\s+(all\s+)?(previous|above|prior)", 0.8),
            (r"(?i)forget\s+(all\s+)?(instructions|rules)", 0.8),
            (r"(?i)(system|developer|user)\s+(prompt|instruction)", 0.9),
            (r"(?i)pretend\s+you\s+are", 0.6),
            (r"(?i)act\s+as\s+(if|though)", 0.6),
            (r"(?i)you\s+are\s+now", 0.5),
            (r"(?i)show\s+me\s+your\s+(prompt|instructions)", 0.9),
            (r"(?i)what\s+is\s+your\s+(system\s+)?prompt", 0.9),
            (r"(?i)print\s+your\s+(initial|original)", 0.8),
            (r"(?i)repeat\s+(the\s+)?(word|phrase)", 0.4),
            (r"(?i)says?\s+the\s+following", 0.4),
            (r"<\|.*?\|>", 0.7),
        ]
        
        self.blocked_keywords = [
            "sudo", "rm -rf", "drop database", "delete from",
            "alter table", "shutdown", "reboot", "format",
            "encrypt", "ransomware", "malware", "exploit"
        ]
    
    def detect(self, text: str) -> Tuple[bool, float, List[str]]:
        """Detect prompt injection"""
        risk_score = 0.0
        detected = []
        
        for pattern, weight in self.injection_patterns:
            if re.search(pattern, text):
                risk_score += weight
                detected.append(f"pattern:{pattern[:20]}")
        
        text_lower = text.lower()
        for keyword in self.blocked_keywords:
            if keyword in text_lower:
                risk_score += 0.9
                detected.append(f"keyword:{keyword}")
        
        if re.search(r'\\x[0-9a-f]{2}', text):
            risk_score += 0.7
            detected.append("hex_encoding")
        
        if len(text) > 2000:
            risk_score += 0.3
        
        risk_score = min(risk_score, 1.0)
        is_safe = risk_score < 0.7
        
        return is_safe, risk_score, detected
    
    def sanitize(self, text: str) -> str:
        """Sanitize input"""
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'```.*?```', '[CODE_BLOCK]', text, flags=re.DOTALL)
        text = re.sub(r'[^\w\s,.!?\-:;()[\]{}]', '', text)
        
        if len(text) > 2000:
            text = text[:2000] + "... [TRUNCATED]"
        
        return text