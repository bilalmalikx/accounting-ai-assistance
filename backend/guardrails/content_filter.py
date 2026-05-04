"""Content Filter for Profanity and Inappropriate Content"""
import re
from typing import Tuple, List

class ContentFilter:
    def __init__(self):
        self.profanity_list = [
            'fuck', 'shit', 'asshole', 'bitch', 'damn', 'hell',
            'bastard', 'crap', 'dick', 'piss', 'slut', 'whore'
        ]
        
        self.inappropriate_patterns = [
            (r'(?i)violence|kill|murder|attack', "violence"),
            (r'(?i)hate\s+(speech|crime|group)', "hate_speech"),
            (r'(?i)terrorism|bomb|explosive', "terrorism"),
            (r'(?i)drugs|cocaine|heroin|marijuana', "drugs"),
        ]
    
    def filter(self, text: str) -> Tuple[bool, List[str]]:
        """Filter content and return (is_clean, violations)"""
        violations = []
        text_lower = text.lower()
        
        for word in self.profanity_list:
            if word in text_lower:
                violations.append(f"profanity:{word}")
        
        for pattern, violation_type in self.inappropriate_patterns:
            if re.search(pattern, text_lower):
                violations.append(violation_type)
        
        is_clean = len(violations) == 0
        return is_clean, violations
    
    def censor(self, text: str) -> str:
        """Censor inappropriate content"""
        censored = text
        
        for word in self.profanity_list:
            censored = re.sub(f'(?i){word}', '*' * len(word), censored)
        
        return censored