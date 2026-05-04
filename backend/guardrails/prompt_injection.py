class PromptInjectionDetector:
    def detect(self, text: str) -> bool:
        injection_patterns = [
            "ignore previous", "forget instructions",
            "system prompt", "you are now", "pretend"
        ]
        
        text_lower = text.lower()
        for pattern in injection_patterns:
            if pattern in text_lower:
                return True
        return False