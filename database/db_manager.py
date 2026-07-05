"""
db_manager.py - SQLite database manager with full schema.
"""
from __future__ import annotations
import sqlite3
import logging
from pathlib import Path
from config import settings

log = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DATABASE_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE, return lastrowid or rowcount."""
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid or cur.rowcount


def fetchone(sql: str, params: tuple = ()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone()


def fetchall(sql: str, params: tuple = ()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    browser TEXT DEFAULT 'chrome',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    steps_json TEXT DEFAULT '[]',
    enabled INTEGER DEFAULT 1,
    module TEXT DEFAULT 'General',
    group_name TEXT DEFAULT 'Default',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    test_case_id INTEGER REFERENCES test_cases(id) ON DELETE SET NULL,
    test_name TEXT NOT NULL,
    url TEXT,
    status TEXT DEFAULT 'pending',
    pass INTEGER DEFAULT 0,
    fail INTEGER DEFAULT 0,
    flaky INTEGER DEFAULT 0,
    duration_seconds REAL DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    screenshot_path TEXT,
    log_output TEXT,
    stack_trace TEXT,
    browser TEXT DEFAULT 'chrome',
    os_info TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME
);

CREATE TABLE IF NOT EXISTS retries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER REFERENCES executions(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    status TEXT DEFAULT 'fail',
    error_message TEXT,
    screenshot_path TEXT,
    duration_seconds REAL DEFAULT 0,
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER REFERENCES executions(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL,
    file_path TEXT,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER REFERENCES executions(id) ON DELETE CASCADE,
    root_cause TEXT,
    suggested_fix TEXT,
    severity TEXT DEFAULT 'medium',
    confidence_score REAL DEFAULT 0.0,
    recommendations TEXT,
    model_used TEXT,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS website_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flaky_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER REFERENCES test_cases(id) ON DELETE CASCADE,
    score REAL DEFAULT 0.0,
    verdict TEXT DEFAULT 'stable',
    last_calculated DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db():
    """Initialize database schema."""
    settings.ensure_directories()
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    log.info("Database initialized at %s", settings.DATABASE_PATH)
