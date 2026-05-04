import sqlite3
import json
from datetime import datetime
from pathlib import Path
from backend.utils.logger import logger

class AuditService:
    def __init__(self):
        self.db_path = Path("./data/audit.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_ip TEXT,
                query TEXT,
                response TEXT,
                sources TEXT,
                duration REAL,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_ip TEXT,
                filename TEXT,
                chunks INTEGER,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def log_query(self, query: str, response: str, sources: list, duration: float, user_ip: str, status: str = "success"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO query_logs (timestamp, user_ip, query, response, sources, duration, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_ip,
            query[:500],
            response[:1000],
            json.dumps(sources),
            duration,
            status
        ))
        
        conn.commit()
        conn.close()
    
    async def log_document_upload(self, filename: str, chunks: int, user_ip: str, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO document_logs (timestamp, user_ip, filename, chunks, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_ip,
            filename,
            chunks,
            status
        ))
        
        conn.commit()
        conn.close()

audit_service = AuditService()