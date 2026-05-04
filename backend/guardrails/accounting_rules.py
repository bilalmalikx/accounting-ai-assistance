"""Domain-Specific Accounting Rules and Validation"""
import re
from typing import Tuple, Dict, List

class AccountingRulesGuard:
    def __init__(self):
        self.allowed_terms = [
            'balance sheet', 'profit loss', 'p&l', 'trial balance',
            'ledger', 'journal', 'invoice', 'bill', 'receipt',
            'payment', 'transaction', 'debit', 'credit',
            'gst', 'tax', 'tds', 'income tax', 'audit',
            'statement', 'account', 'fiscal year', 'financial year',
            'expense', 'revenue', 'asset', 'liability', 'equity'
        ]
        
        self.sensitive_operations = [
            'delete', 'remove', 'modify', 'update', 'change',
            'alter', 'override', 'bypass', 'hide'
        ]
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate if query is within accounting domain"""
        query_lower = query.lower()
        
        # Check sensitive operations
        for op in self.sensitive_operations:
            if op in query_lower and not self._has_permission_context(query_lower):
                return False, f"Query contains sensitive operation: '{op}'"
        
        # Check accounting terms
        has_term = any(term in query_lower for term in self.allowed_terms)
        
        if not has_term:
            generic_patterns = [
                r'(amount|total|sum|balance)',
                r'(date|month|year|february|march)',
                r'(company|firm|entity)',
                r'(statement|report|document)'
            ]
            if not any(re.search(p, query_lower) for p in generic_patterns):
                return True, "Query is acceptable"
        
        return True, "Query validated"
    
    def _has_permission_context(self, query: str) -> bool:
        permission_patterns = [
            r'can i delete', r'how to delete', r'delete permission',
            r'authorized to delete', r'allowed to delete'
        ]
        return any(re.search(p, query) for p in permission_patterns)
    
    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities"""
        entities = {
            'amounts': [],
            'dates': [],
            'companies': [],
            'document_types': []
        }
        
        # Extract amounts
        amount_pattern = r'(?:rs|inr|₹)\s*([\d,]+\.?\d*)|([\d,]+\.?\d*)\s*(?:rs|inr)'
        matches = re.findall(amount_pattern, text, re.IGNORECASE)
        for match in matches:
            amount = match[0] or match[1]
            if amount:
                entities['amounts'].append(amount.replace(',', ''))
        
        # Extract dates
        date_pattern = r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
        entities['dates'].extend(re.findall(date_pattern, text, re.IGNORECASE))
        
        return entities
    
    def is_financial_query(self, query: str) -> bool:
        """Check if query is financial"""
        financial_keywords = [
            'profit', 'loss', 'revenue', 'expense', 'cost', 'income',
            'asset', 'liability', 'equity', 'cash', 'bank', 'loan',
            'interest', 'depreciation', 'tax', 'gst', 'invoice'
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in financial_keywords)