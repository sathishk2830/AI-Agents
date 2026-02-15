import sqlite3
from pathlib import Path
import os

DB_PATH = os.getenv("DATABASE_PATH", "./app.db")

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema from gemini.md"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Jira Config Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jira_config (
            id INTEGER PRIMARY KEY,
            domain TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            api_token TEXT NOT NULL,
            connection_status TEXT DEFAULT 'untested',
            last_tested_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # LLM Config Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_config (
            id INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,
            grok_api_key TEXT,
            grok_model TEXT DEFAULT 'grok-2',
            grok_temperature REAL DEFAULT 0.7,
            grok_max_tokens INTEGER DEFAULT 2000,
            ollama_url TEXT DEFAULT 'http://localhost:11434',
            ollama_model TEXT,
            connection_status TEXT DEFAULT 'untested',
            last_tested_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Template Config Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS template_config (
            id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL UNIQUE,
            file_content TEXT,
            file_format TEXT,
            validation_status TEXT DEFAULT 'untested',
            last_tested_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Generation History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generation_history (
            id TEXT PRIMARY KEY,
            jira_issue_id TEXT NOT NULL,
            jira_summary TEXT,
            generated_content TEXT NOT NULL,
            provider_used TEXT,
            generation_time_seconds REAL,
            token_usage INTEGER,
            template_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"✅ Database initialized at {DB_PATH}")
