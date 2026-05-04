#!/usr/bin/env python
import sqlite3
from pathlib import Path

Path("./data").mkdir(exist_ok=True)

conn = sqlite3.connect("./data/audit.db")
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

print("✅ Database initialized")