"""Complete Query Service with RAG + Guardrails + Audit"""
import time
from typing import Dict, Any, List, Optional
from backend.core.vector_store import VectorStoreManager
from backend.core.llm import LLMManager
from backend.guardrails.input_guard import InputGuard
from backend.guardrails.output_guard import OutputGuard
from backend.guardrails.pii_detector import PIIDetector
from backend.guardrails.prompt_injection import PromptInjectionDetector
from backend.guardrails.accounting_rules import AccountingRulesGuard
from backend.guardrails.content_filter import ContentFilter
from backend.utils.helpers import extract_numbers, parse_date_from_text, truncate_text
from backend.services.audit_service import AuditService
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.llm = LLMManager()
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()
        self.pii_detector = PIIDetector()
        self.prompt_injection = PromptInjectionDetector()
        self.accounting_rules = AccountingRulesGuard()
        self.content_filter = ContentFilter()
        self.audit_service = AuditService()
    
    async def answer_query(self, query: str, top_k: int = 5, 
                          filter_category: str = None, filter_tags: List[str] = None,
                          client_ip: str = "unknown", user_agent: str = "unknown",
                          session_id: str = None) -> Dict[str, Any]:
        """Answer accounting query with full guardrails"""
        
        start_time = time.time()
        
        # ========== LAYER 1: INPUT GUARDRAILS ==========
        is_safe, risk_score, guardrail_details = self.input_guard.validate(query)
        
        if not is_safe:
            self.audit_service.log_query(
                query=query,
                response="Query blocked by input guardrails",
                processing_time_ms=(time.time() - start_time) * 1000,
                client_ip=client_ip,
                status="blocked",
                risk_score=risk_score,
                guardrail_issues=guardrail_details.get('issues', [])
            )
            
            return {
                "answer": f"⚠️ Query blocked due to security concerns. Risk score: {risk_score}",
                "sources": [],
                "scores": [],
                "processing_time_ms": (time.time() - start_time) * 1000,
                "blocked": True,
                "risk_score": risk_score
            }
        
        # ========== LAYER 2: DOMAIN VALIDATION ==========
        if settings.ENABLE_ACCOUNTING_RULES:
            is_valid, domain_message = self.accounting_rules.validate_query(query)
            if not is_valid:
                return {
                    "answer": f"📋 Query not allowed: {domain_message}",
                    "sources": [],
                    "scores": [],
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "blocked": True
                }
        
        # ========== LAYER 3: CONTENT FILTERING ==========
        is_clean, content_violations = self.content_filter.filter(query)
        if not is_clean:
            logger.warning(f"Content violations: {content_violations}")
        
        # ========== LAYER 4: SANITIZE QUERY ==========
        sanitized_query = self.input_guard.sanitize_query(query)
        
        # ========== LAYER 5: RETRIEVAL ==========
        filter_dict = {}
        if filter_category:
            filter_dict["category"] = filter_category
        if filter_tags:
            filter_dict["tags"] = filter_tags
        
        results = self.vector_store.search(sanitized_query, top_k, filter_dict if filter_dict else None)
        
        if not results:
            return {
                "answer": "📄 No relevant documents found. Please upload accounting files first.",
                "sources": [],
                "scores": [],
                "processing_time_ms": (time.time() - start_time) * 1000
            }
        
        # ========== LAYER 6: CONTEXT PREPARATION ==========
        context_parts = []
        sources = []
        scores = []
        
        for doc, score in results:
            content = doc.page_content
            numbers = extract_numbers(content)
            
            enriched_content = content
            if numbers:
                enriched_content += f"\n[📊 Extracted amounts: {', '.join(numbers[:5])}]"
            
            context_parts.append(enriched_content)
            sources.append({
                "content": truncate_text(content, 300),
                "source": doc.metadata.get("source", "unknown"),
                "category": doc.metadata.get("category", "general"),
                "relevance_score": round(score, 3)
            })
            scores.append(score)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # ========== LAYER 7: LLM GENERATION ==========
        answer = await self.llm.generate(sanitized_query, context)
        
        # ========== LAYER 8: OUTPUT GUARDRAILS ==========
        is_safe_output, output_issues = self.output_guard.validate(answer)
        if not is_safe_output:
            answer = "⚠️ I cannot provide that information due to content safety guidelines."
        
        # Redact PII
        answer, detected_pii = self.pii_detector.redact(answer)
        
        # Sanitize output
        answer = self.output_guard.sanitize(answer)
        
        # Censor profanity
        is_clean, profanity = self.content_filter.filter(answer)
        if not is_clean:
            answer = self.content_filter.censor(answer)
        
        # Add disclaimer
        is_financial = self.accounting_rules.is_financial_query(query)
        answer = self.output_guard.add_disclaimer(answer, is_financial)
        
        # ========== LAYER 9: EXTRACT INSIGHTS ==========
        extracted_amounts = extract_numbers(answer)
        
        # ========== LAYER 10: AUDIT LOGGING ==========
        processing_time_ms = (time.time() - start_time) * 1000
        self.audit_service.log_query(
            query=query,
            response=answer,
            processing_time_ms=processing_time_ms,
            client_ip=client_ip,
            status="success" if not output_issues else "filtered",
            risk_score=risk_score,
            guardrail_issues=guardrail_details.get('issues', []) + output_issues,
            sources_used=[s.get('source') for s in sources]
        )
        
        if session_id:
            self.audit_service.log_query_history(
                query=query,
                answer=answer,
                session_id=session_id,
                processing_time_ms=processing_time_ms
            )
        
        logger.info(f"Query processed: {query[:50]}... | Time: {processing_time_ms:.0f}ms | Risk: {risk_score}")
        
        return {
            "answer": answer,
            "sources": sources,
            "scores": scores,
            "processing_time_ms": processing_time_ms,
            "filtered": len(output_issues) > 0,
            "pii_redacted": len(detected_pii) > 0,
            "extracted_amounts": extracted_amounts,
            "has_financial_data": len(extracted_amounts) > 0,
            "warning": "Content filtered" if not is_clean else None
        }
    
    async def answer_with_context(self, query: str, history: List[Dict], 
                                   top_k: int = 5, client_ip: str = "unknown",
                                   session_id: str = None) -> Dict[str, Any]:
        """Answer with conversation context"""
        
        history_context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in history[-6:]
        ])
        
        contextual_query = f"Previous conversation:\n{history_context}\n\nCurrent: {query}"
        
        return await self.answer_query(contextual_query, top_k, client_ip=client_ip, session_id=session_id)
    
    async def extract_financial_data(self, query: str, client_ip: str = "unknown") -> Dict[str, Any]:
        """Extract structured financial data"""
        
        result = await self.answer_query(query, client_ip=client_ip)
        
        if not result.get("error") and not result.get("blocked"):
            numbers = extract_numbers(result["answer"])
            entities = self.accounting_rules.extract_financial_entities(result["answer"])
            
            result["structured_data"] = {
                "amounts": numbers,
                "dates": entities.get("dates", []),
                "has_amounts": len(numbers) > 0
            }
        
        return result