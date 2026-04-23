from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from .settings import Settings


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Database:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self, settings: Settings) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    api_key TEXT NOT NULL DEFAULT '',
                    base_url TEXT NOT NULL,
                    usage_path TEXT NOT NULL,
                    model TEXT NOT NULL,
                    default_size TEXT NOT NULL,
                    default_quality TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS image_history (
                    id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL CHECK (mode IN ('generate', 'edit')),
                    prompt TEXT NOT NULL,
                    model TEXT NOT NULL,
                    size TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('succeeded', 'failed')),
                    image_url TEXT,
                    image_path TEXT,
                    input_image_url TEXT,
                    input_image_path TEXT,
                    revised_prompt TEXT,
                    usage_json TEXT,
                    provider_response_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ledger_entries (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    amount REAL NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    description TEXT NOT NULL,
                    history_id TEXT,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(history_id) REFERENCES image_history(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS inspiration_prompts (
                    id TEXT PRIMARY KEY,
                    source_url TEXT NOT NULL,
                    source_item_id TEXT NOT NULL,
                    section TEXT NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT,
                    prompt TEXT NOT NULL,
                    image_url TEXT,
                    source_link TEXT,
                    raw_json TEXT,
                    synced_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(source_url, source_item_id)
                );

                CREATE INDEX IF NOT EXISTS idx_image_history_created_at ON image_history(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_ledger_entries_created_at ON ledger_entries(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_inspiration_prompts_synced_at ON inspiration_prompts(synced_at DESC);
                CREATE INDEX IF NOT EXISTS idx_inspiration_prompts_section ON inspiration_prompts(section);
                """
            )
            existing = conn.execute("SELECT id FROM app_config WHERE id = 1").fetchone()
            if existing is None:
                now = utc_now()
                conn.execute(
                    """
                    INSERT INTO app_config (
                        id, api_key, base_url, usage_path, model, default_size,
                        default_quality, user_name, created_at, updated_at
                    )
                    VALUES (1, '', ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        settings.provider_base_url,
                        settings.provider_usage_path,
                        settings.image_model,
                        settings.default_size,
                        settings.default_quality,
                        settings.user_name,
                        now,
                        now,
                    ),
                )

    def get_config(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM app_config WHERE id = 1").fetchone()
            if row is None:
                raise RuntimeError("app_config was not initialized")
            return dict(row)

    def update_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        allowed = {
            "api_key",
            "base_url",
            "usage_path",
            "model",
            "default_size",
            "default_quality",
            "user_name",
        }
        updates = {key: value for key, value in payload.items() if key in allowed and value is not None}
        if not updates:
            return self.get_config()

        updates["updated_at"] = utc_now()
        assignments = ", ".join(f"{key} = ?" for key in updates)
        values = list(updates.values())
        with self.connect() as conn:
            conn.execute(f"UPDATE app_config SET {assignments} WHERE id = 1", values)
        return self.get_config()

    def create_history(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        record = {
            "id": payload.get("id") or uuid4().hex,
            "mode": payload["mode"],
            "prompt": payload["prompt"],
            "model": payload["model"],
            "size": payload["size"],
            "quality": payload["quality"],
            "status": payload["status"],
            "image_url": payload.get("image_url"),
            "image_path": payload.get("image_path"),
            "input_image_url": payload.get("input_image_url"),
            "input_image_path": payload.get("input_image_path"),
            "revised_prompt": payload.get("revised_prompt"),
            "usage_json": _json_or_none(payload.get("usage")),
            "provider_response_json": _json_or_none(payload.get("provider_response")),
            "error": payload.get("error"),
            "created_at": now,
            "updated_at": now,
        }
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO image_history (
                    id, mode, prompt, model, size, quality, status, image_url, image_path,
                    input_image_url, input_image_path, revised_prompt, usage_json,
                    provider_response_json, error, created_at, updated_at
                )
                VALUES (
                    :id, :mode, :prompt, :model, :size, :quality, :status, :image_url,
                    :image_path, :input_image_url, :input_image_path, :revised_prompt,
                    :usage_json, :provider_response_json, :error, :created_at, :updated_at
                )
                """,
                record,
            )
        return self.get_history(record["id"])

    def get_history(self, history_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM image_history WHERE id = ?", (history_id,)).fetchone()
        return _history_row(row) if row else None

    def list_history(self, limit: int = 30, offset: int = 0, q: str = "") -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        search = f"%{q.strip().lower()}%"
        with self.connect() as conn:
            if q.strip():
                rows = conn.execute(
                    """
                    SELECT * FROM image_history
                    WHERE lower(prompt) LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (search, limit, offset),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM image_history
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                ).fetchall()
        return [_history_row(row) for row in rows]

    def delete_history(self, history_id: str) -> bool:
        with self.connect() as conn:
            result = conn.execute("DELETE FROM image_history WHERE id = ?", (history_id,))
            return result.rowcount > 0

    def add_ledger_entry(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": payload.get("id") or uuid4().hex,
            "event_type": payload["event_type"],
            "amount": payload.get("amount", 0),
            "currency": payload.get("currency", "USD"),
            "description": payload["description"],
            "history_id": payload.get("history_id"),
            "metadata_json": _json_or_none(payload.get("metadata")),
            "created_at": utc_now(),
        }
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO ledger_entries (
                    id, event_type, amount, currency, description, history_id,
                    metadata_json, created_at
                )
                VALUES (
                    :id, :event_type, :amount, :currency, :description, :history_id,
                    :metadata_json, :created_at
                )
                """,
                record,
            )
        return record

    def list_ledger(self, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM ledger_entries ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_ledger_row(row) for row in rows]

    def upsert_inspirations(self, source_url: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        now = utc_now()
        changed = 0
        with self.connect() as conn:
            for item in items:
                record = {
                    "id": item["id"],
                    "source_url": source_url,
                    "source_item_id": item["source_item_id"],
                    "section": item["section"],
                    "title": item["title"],
                    "author": item.get("author"),
                    "prompt": item["prompt"],
                    "image_url": item.get("image_url"),
                    "source_link": item.get("source_link"),
                    "raw_json": _json_or_none(item.get("raw")),
                    "synced_at": now,
                    "created_at": now,
                    "updated_at": now,
                }
                conn.execute(
                    """
                    INSERT INTO inspiration_prompts (
                        id, source_url, source_item_id, section, title, author, prompt,
                        image_url, source_link, raw_json, synced_at, created_at, updated_at
                    )
                    VALUES (
                        :id, :source_url, :source_item_id, :section, :title, :author,
                        :prompt, :image_url, :source_link, :raw_json, :synced_at,
                        :created_at, :updated_at
                    )
                    ON CONFLICT(source_url, source_item_id) DO UPDATE SET
                        section = excluded.section,
                        title = excluded.title,
                        author = excluded.author,
                        prompt = excluded.prompt,
                        image_url = excluded.image_url,
                        source_link = excluded.source_link,
                        raw_json = excluded.raw_json,
                        synced_at = excluded.synced_at,
                        updated_at = excluded.updated_at
                    """,
                    record,
                )
                changed += 1
        return {"count": changed, "synced_at": now}

    def list_inspirations(
        self,
        limit: int = 48,
        offset: int = 0,
        q: str = "",
        section: str = "",
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        clauses = []
        params: list[Any] = []
        if q.strip():
            clauses.append("(lower(title) LIKE ? OR lower(prompt) LIKE ? OR lower(author) LIKE ?)")
            search = f"%{q.strip().lower()}%"
            params.extend([search, search, search])
        if section.strip():
            clauses.append("section = ?")
            params.append(section.strip())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM inspiration_prompts
                {where}
                ORDER BY synced_at DESC, section ASC, title ASC
                LIMIT ? OFFSET ?
                """,
                (*params, limit, offset),
            ).fetchall()
        return [_inspiration_row(row) for row in rows]

    def inspiration_stats(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    MAX(synced_at) AS last_synced_at,
                    COUNT(DISTINCT section) AS sections
                FROM inspiration_prompts
                """
            ).fetchone()
            section_rows = conn.execute(
                """
                SELECT section, COUNT(*) AS count
                FROM inspiration_prompts
                GROUP BY section
                ORDER BY section ASC
                """
            ).fetchall()
        return {
            "total": int(row["total"] or 0),
            "last_synced_at": row["last_synced_at"],
            "sections": int(row["sections"] or 0),
            "section_counts": [{"section": item["section"], "count": int(item["count"])} for item in section_rows],
        }

    def stats(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) AS succeeded,
                    SUM(CASE WHEN mode = 'edit' THEN 1 ELSE 0 END) AS edits,
                    MAX(created_at) AS last_generation_at
                FROM image_history
                """
            ).fetchone()
        return {
            "total": int(row["total"] or 0),
            "succeeded": int(row["succeeded"] or 0),
            "edits": int(row["edits"] or 0),
            "last_generation_at": row["last_generation_at"],
        }


def _json_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _json_load(value: str | None) -> Any:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _history_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["usage"] = _json_load(data.pop("usage_json"))
    data["provider_response"] = _json_load(data.pop("provider_response_json"))
    return data


def _ledger_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["metadata"] = _json_load(data.pop("metadata_json"))
    return data


def _inspiration_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["raw"] = _json_load(data.pop("raw_json"))
    return data
