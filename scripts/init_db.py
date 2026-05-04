#!/usr/bin/env python
"""Initialize Database Script"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.session import init_db
from backend.config import settings

def main():
    print(f"Initializing database at {settings.AUDIT_DB_PATH}")
    init_db()
    print("✅ Database initialized successfully")
    print(f"   Tables created: audit_logs, query_history, documents, feedback_records, security_events")

if __name__ == "__main__":
    main()