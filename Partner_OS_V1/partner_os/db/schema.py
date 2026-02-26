"""SQLite schema DDL."""

from __future__ import annotations

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS deals (
    deal_id TEXT PRIMARY KEY,
    property_address TEXT NOT NULL,
    slug TEXT NOT NULL,
    status TEXT NOT NULL,
    jurisdiction_warning INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    underwriting_json TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id TEXT NOT NULL,
    category TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    summary TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id TEXT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS library_index (
    ref_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    doctrine_abstract TEXT NOT NULL,
    indexed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    deal_id TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_runs (
    run_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    deal_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS action_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    deal_id TEXT,
    action TEXT NOT NULL,
    rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
    status TEXT NOT NULL,
    details_json TEXT,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS api_calls (
    call_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_type TEXT NOT NULL,
    status TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    error_message TEXT,
    deal_id TEXT,
    details_json TEXT,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE SET NULL
);
"""
