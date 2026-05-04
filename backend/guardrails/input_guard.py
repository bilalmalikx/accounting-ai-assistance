"""Complete Input Guardrail - PII, Injection, Domain Validation"""
import re
from typing import Tuple, Dict, List
from backend.guardrails.pii_detector import PIIDetector
from backend.guardrails.prompt_injection import PromptInjectionDetector
from backend.guardrails.accounting_rules import AccountingRulesGuard
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class InputGuard:
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.prompt_injection = PromptInjectionDetector()
        self.accounting_rules = AccountingRulesGuard()
        
        self.blacklisted_words = [
            'hack', 'crack', 'exploit', 'bypass', 'circumvent',
            'illegal', 'fraud', 'scam', 'cheat', 'steal'
        ]
        
        self.max_length = 2000
        self.min_length = 2
    
    def validate(self, query: str) -> Tuple[bool, float, Dict]:
        """Validate input query - returns (is_safe, risk_score, details)"""
        risk_score = 0.0
        issues = []
        
        # Empty query
        if not query or len(query.strip()) < self.min_length:
            return False, 0.9, {"issue": "query_too_short", "message": "Query is too short"}
        
        # Length check
        if len(query) > self.max_length:
            risk_score += 0.3
            issues.append("query_too_long")
        
        # Blacklisted words
        query_lower = query.lower()
        for word in self.blacklisted_words:
            if word in query_lower:
                risk_score += 0.5
                issues.append(f"blacklisted:{word}")
        
        # Prompt injection
        is_safe_pi, pi_score, pi_patterns = self.prompt_injection.detect(query)
        if not is_safe_pi:
            risk_score += pi_score
            issues.extend(pi_patterns)
        
        # PII detection
        if settings.ENABLE_PII_DETECTION:
            pii_detected = self.pii_detector.detect(query)
            if pii_detected:
                risk_score += 0.3
                issues.append(f"pii_detected:{len(pii_detected)}")
            
            if self.pii_detector.has_sensitive_pii(query):
                risk_score += 0.6
                issues.append("sensitive_pii")
        
        # Accounting rules
        if settings.ENABLE_ACCOUNTING_RULES:
            is_valid, domain_msg = self.accounting_rules.validate_query(query)
            if not is_valid:
                risk_score += 0.4
                issues.append("domain_violation")
        
        # Special character overload
        special_chars = sum(1 for c in query if not c.isalnum() and not c.isspace())
        if special_chars > len(query) * 0.3:
            risk_score += 0.2
            issues.append("special_chars")
        
        risk_score = min(risk_score, 1.0)
        is_safe = risk_score < settings.INPUT_GUARD_THRESHOLD
        
        details = {
            "issues": issues,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low",
            "query_length": len(query)
        }
        
        if not is_safe:
            logger.warning(f"Input blocked - Risk: {risk_score}, Issues: {issues}")
        
        return is_safe, risk_score, details
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize query"""
        query = re.sub(r'\s+', ' ', query)
        query = re.sub(r'[!@#$%^&*()]{3,}', '', query)
        query = query.replace('\x00', '')
        return query.strip()