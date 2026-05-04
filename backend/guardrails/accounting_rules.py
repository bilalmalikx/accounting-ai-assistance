class AccountingRules:
    @staticmethod
    def is_accounting_query(query: str) -> bool:
        keywords = ["audit", "tax", "gst", "invoice", "balance", "profit", "loss", "statement"]
        return any(k in query.lower() for k in keywords)