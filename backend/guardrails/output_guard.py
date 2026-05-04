"""Complete Output Guardrail - Safety and Content Filtering"""
import re
from typing import Tuple, List, Dict
from backend.guardrails.pii_detector import PIIDetector
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class OutputGuard:
    def __init__(self):
        self.pii_detector = PIIDetector()
        
        self.unsafe_patterns = [
            (r'(?i)(how to|tutorial|guide).*(hack|exploit|bypass)', "security_guidance"),
            (r'(?i)(illegal|fraud|scam).*(method|way)', "illegal_content"),
            (r'(?i)step by step.*(break|circumvent)', "procedural_attack"),
            (r'(?i)(make|create).*(virus|malware)', "malware"),
            (r'(?i)(steal|theft).*(money|account)', "theft"),
            (r'(?i)credit card.*\d{4}', "credit_card_leak"),
            (r'(?i)ssn|social security.*\d{3}', "ssn_leak"),
        ]
        
        self.max_length = 2000
    
    def validate(self, output: str) -> Tuple[bool, List[str]]:
        """Validate output safety"""
        issues = []
        
        for pattern, issue_type in self.unsafe_patterns:
            if re.search(pattern, output):
                issues.append(issue_type)
                logger.warning(f"Unsafe output pattern: {issue_type}")
        
        if settings.ENABLE_PII_DETECTION:
            pii_detected = self.pii_detector.detect(output)
            if pii_detected:
                issues.append(f"pii_leakage:{len(pii_detected)}")
            
            if self.pii_detector.has_sensitive_pii(output):
                issues.append("sensitive_pii_leakage")
        
        if len(output) > self.max_length:
            issues.append("output_too_long")
        
        is_safe = len(issues) < 2  # Allow some issues but not many
        return is_safe, issues
    
    def sanitize(self, output: str) -> str:
        """Sanitize output"""
        # Redact PII
        redacted, _ = self.pii_detector.redact(output)
        
        # Remove multiple newlines
        redacted = re.sub(r'\n{3,}', '\n\n', redacted)
        
        # Trim if too long
        if len(redacted) > self.max_length:
            redacted = redacted[:self.max_length] + "... [truncated]"
        
        return redacted
    
    def add_disclaimer(self, output: str, is_financial: bool = True) -> str:
        """Add appropriate disclaimer"""
        if is_financial:
            disclaimer = "\n\n---\n*Disclaimer: Information extracted from uploaded documents. Please verify with original sources.*"
            return output + disclaimer
        return output