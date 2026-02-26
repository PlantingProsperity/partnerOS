"""SQLite persistence and repositories."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from partner_os.db.schema import SCHEMA_SQL


class DataStore:
    """Repository facade for Partner OS state."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.database_path, check_same_thread=False)
        self._in_transaction = False
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._conn.executescript(SCHEMA_SQL)
        self._commit_if_needed()

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Atomic transaction context."""
        try:
            self._in_transaction = True
            self._conn.execute("BEGIN")
            yield self._conn
            self._commit_if_needed()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            self._in_transaction = False

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _commit_if_needed(self) -> None:
        if not self._in_transaction:
            self._conn.commit()

    def create_deal(self, deal_id: str, property_address: str, slug: str, jurisdiction_warning: bool) -> None:
        now = self.now_iso()
        self._conn.execute(
            """
            INSERT INTO deals (deal_id, property_address, slug, status, jurisdiction_warning, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (deal_id, property_address, slug, "new", int(jurisdiction_warning), now, now),
        )
        self._commit_if_needed()

    def update_deal_status(self, deal_id: str, status: str, notes: str | None = None) -> None:
        self._conn.execute(
            """
            UPDATE deals
            SET status = ?, notes = COALESCE(?, notes), updated_at = ?
            WHERE deal_id = ?
            """,
            (status, notes, self.now_iso(), deal_id),
        )
        self._commit_if_needed()

    def update_deal_underwriting(self, deal_id: str, underwriting: dict[str, Any]) -> None:
        self._conn.execute(
            """
            UPDATE deals
            SET underwriting_json = ?, updated_at = ?
            WHERE deal_id = ?
            """,
            (json.dumps(underwriting, sort_keys=True), self.now_iso(), deal_id),
        )
        self._commit_if_needed()

    def get_deal(self, deal_id: str) -> sqlite3.Row | None:
        cur = self._conn.execute("SELECT * FROM deals WHERE deal_id = ?", (deal_id,))
        return cur.fetchone()

    def list_deals(self) -> list[sqlite3.Row]:
        cur = self._conn.execute("SELECT * FROM deals ORDER BY created_at DESC")
        return cur.fetchall()

    def insert_document(self, deal_id: str, category: str, file_path: Path, summary: str | None) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO documents (deal_id, category, file_path, summary, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (deal_id, category, str(file_path), summary, self.now_iso()),
        )
        self._commit_if_needed()
        return int(cur.lastrowid)

    def list_documents(self, deal_id: str) -> list[sqlite3.Row]:
        cur = self._conn.execute(
            "SELECT * FROM documents WHERE deal_id = ? ORDER BY created_at ASC",
            (deal_id,),
        )
        return cur.fetchall()

    def insert_chat_message(self, role: str, content: str, deal_id: str | None = None) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO chat_messages (deal_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (deal_id, role, content, self.now_iso()),
        )
        self._commit_if_needed()
        return int(cur.lastrowid)

    def list_chat_messages(self, limit: int = 100) -> list[sqlite3.Row]:
        cur = self._conn.execute(
            "SELECT * FROM chat_messages ORDER BY message_id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()[::-1]

    def upsert_library_entry(self, ref_id: str, title: str, file_path: Path, doctrine_abstract: str) -> None:
        self._conn.execute(
            """
            INSERT INTO library_index (ref_id, title, file_path, doctrine_abstract, indexed_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(ref_id) DO UPDATE SET
                title=excluded.title,
                file_path=excluded.file_path,
                doctrine_abstract=excluded.doctrine_abstract,
                indexed_at=excluded.indexed_at
            """,
            (ref_id, title, str(file_path), doctrine_abstract, self.now_iso()),
        )
        self._commit_if_needed()

    def search_library(self, query: str, limit: int = 5) -> list[sqlite3.Row]:
        like_query = f"%{query}%"
        cur = self._conn.execute(
            """
            SELECT * FROM library_index
            WHERE title LIKE ? OR doctrine_abstract LIKE ?
            ORDER BY indexed_at DESC
            LIMIT ?
            """,
            (like_query, like_query, limit),
        )
        return cur.fetchall()

    def insert_task(self, task_id: str, deal_id: str, task_type: str, payload: dict[str, Any], status: str) -> None:
        now = self.now_iso()
        self._conn.execute(
            """
            INSERT INTO tasks (task_id, deal_id, task_type, status, payload_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (task_id, deal_id, task_type, status, json.dumps(payload, sort_keys=True), now, now),
        )
        self._commit_if_needed()

    def update_task_status(self, task_id: str, status: str) -> None:
        self._conn.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
            (status, self.now_iso(), task_id),
        )
        self._commit_if_needed()

    def get_task(self, task_id: str) -> sqlite3.Row | None:
        cur = self._conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        return cur.fetchone()

    def list_tasks(self, limit: int = 200) -> list[sqlite3.Row]:
        cur = self._conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        return cur.fetchall()

    def create_agent_run(self, task_id: str, deal_id: str, agent_name: str, payload: dict[str, Any]) -> str:
        run_id = str(uuid.uuid4())
        self._conn.execute(
            """
            INSERT INTO agent_runs (run_id, task_id, deal_id, agent_name, status, input_json, started_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, task_id, deal_id, agent_name, "running", json.dumps(payload, sort_keys=True), self.now_iso()),
        )
        self._commit_if_needed()
        return run_id

    def finish_agent_run(self, run_id: str, status: str, output: dict[str, Any] | None = None) -> None:
        self._conn.execute(
            """
            UPDATE agent_runs
            SET status = ?, output_json = ?, finished_at = ?
            WHERE run_id = ?
            """,
            (status, json.dumps(output or {}, sort_keys=True), self.now_iso(), run_id),
        )
        self._commit_if_needed()

    def list_agent_runs(self, limit: int = 200) -> list[sqlite3.Row]:
        cur = self._conn.execute("SELECT * FROM agent_runs ORDER BY started_at DESC LIMIT ?", (limit,))
        return cur.fetchall()

    def log_action(
        self,
        actor: str,
        action: str,
        rationale: str,
        status: str,
        deal_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> int:
        if not rationale or not rationale.strip():
            raise ValueError("Action rationale must be non-empty.")
        cur = self._conn.execute(
            """
            INSERT INTO action_logs (timestamp, actor, deal_id, action, rationale, status, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.now_iso(),
                actor,
                deal_id,
                action,
                rationale.strip(),
                status,
                json.dumps(details or {}, sort_keys=True),
            ),
        )
        self._commit_if_needed()
        return int(cur.lastrowid)

    def list_action_logs(self, limit: int = 200) -> list[sqlite3.Row]:
        cur = self._conn.execute(
            "SELECT * FROM action_logs ORDER BY log_id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()

    def insert_api_call(
        self,
        provider: str,
        model: str,
        endpoint: str,
        request_type: str,
        status: str,
        latency_ms: int,
        deal_id: str | None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
        error_message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        call_id = str(uuid.uuid4())
        self._conn.execute(
            """
            INSERT INTO api_calls (
                call_id, timestamp, provider, model, endpoint, request_type, status,
                latency_ms, prompt_tokens, completion_tokens, total_tokens, error_message,
                deal_id, details_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                call_id,
                self.now_iso(),
                provider,
                model,
                endpoint,
                request_type,
                status,
                latency_ms,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                error_message,
                deal_id,
                json.dumps(details or {}, sort_keys=True),
            ),
        )
        self._commit_if_needed()
        return call_id

    def list_api_calls(self, limit: int = 200) -> list[sqlite3.Row]:
        cur = self._conn.execute(
            "SELECT * FROM api_calls ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()
