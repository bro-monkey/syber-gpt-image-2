from __future__ import annotations

import asyncio
import hashlib
import re
from typing import Any
from urllib.parse import urljoin

import httpx
from fastapi import FastAPI

from .db import Database
from .settings import Settings


HEADING_RE = re.compile(r"^###\s+Case\s+([^:]+):\s+(.+)$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
PROMPT_RE = re.compile(r"\*\*Prompt:\*\*\s*```(?:\w+)?\s*(.*?)\s*```", re.S)
IMAGE_RE = re.compile(r"<img\s+[^>]*src=['\"]([^'\"]+)['\"]", re.I)
LINK_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)")
AUTHOR_RE = re.compile(r"\(by\s+\[@?([^\]]+)\]\(([^)]+)\)\)")


def parse_inspiration_markdown(markdown: str, source_url: str) -> list[dict[str, Any]]:
    lines = markdown.splitlines()
    sections: list[tuple[int, str]] = []
    case_starts: list[tuple[int, str, str]] = []
    current_section = "Uncategorized"

    for index, line in enumerate(lines):
        section_match = SECTION_RE.match(line)
        if section_match and not line.startswith("###"):
            current_section = _clean_heading(section_match.group(1))
            sections.append((index, current_section))
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            case_starts.append((index, current_section, line.strip()))

    items: list[dict[str, Any]] = []
    for position, (start, section, heading) in enumerate(case_starts):
        end = case_starts[position + 1][0] if position + 1 < len(case_starts) else len(lines)
        block = "\n".join(lines[start:end])
        prompt_match = PROMPT_RE.search(block)
        if not prompt_match:
            continue
        prompt = prompt_match.group(1).strip()
        if not prompt:
            continue

        parsed_heading = _parse_case_heading(heading)
        image_match = IMAGE_RE.search(block)
        image_url = _resolve_url(source_url, image_match.group(1)) if image_match else None
        source_item_id = _stable_id(source_url, section, parsed_heading["title"], parsed_heading.get("author"), prompt)

        items.append(
            {
                "id": source_item_id,
                "source_item_id": source_item_id,
                "section": section,
                "title": parsed_heading["title"],
                "author": parsed_heading.get("author"),
                "prompt": prompt,
                "image_url": image_url,
                "source_link": parsed_heading.get("source_link"),
                "raw": {"heading": heading},
            }
        )

    return items


async def sync_inspirations(settings: Settings, db: Database) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        response = await client.get(settings.inspiration_source_url)
        response.raise_for_status()
    items = parse_inspiration_markdown(response.text, settings.inspiration_source_url)
    result = db.upsert_inspirations(settings.inspiration_source_url, items)
    return {
        "ok": True,
        "source_url": settings.inspiration_source_url,
        "parsed": len(items),
        **result,
    }


async def run_inspiration_sync_loop(app: FastAPI) -> None:
    settings: Settings = app.state.settings
    db: Database = app.state.db
    try:
        if settings.inspiration_sync_on_startup:
            await _safe_sync(settings, db, app)
        if settings.inspiration_sync_interval_seconds <= 0:
            return
        while True:
            await asyncio.sleep(settings.inspiration_sync_interval_seconds)
            await _safe_sync(settings, db, app)
    except asyncio.CancelledError:
        raise


async def _safe_sync(settings: Settings, db: Database, app: FastAPI) -> None:
    try:
        app.state.last_inspiration_sync = await sync_inspirations(settings, db)
        app.state.last_inspiration_sync_error = None
    except Exception as exc:  # pragma: no cover - best effort background diagnostics.
        app.state.last_inspiration_sync_error = str(exc)


def _parse_case_heading(heading: str) -> dict[str, str | None]:
    match = HEADING_RE.match(heading)
    rest = match.group(2).strip() if match else heading.replace("###", "", 1).strip()
    author = None
    author_match = AUTHOR_RE.search(rest)
    if author_match:
        author = f"@{author_match.group(1).lstrip('@')}"
        rest = rest[: author_match.start()].strip()

    source_link = None
    title = rest
    link_match = LINK_RE.match(rest)
    if link_match:
        title = link_match.group(1).strip()
        source_link = link_match.group(2).strip()
    return {"title": _clean_heading(title), "author": author, "source_link": source_link}


def _clean_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("#", "").strip())


def _stable_id(*parts: str | None) -> str:
    raw = "\n".join(part or "" for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _resolve_url(source_url: str, url: str) -> str:
    return urljoin(source_url, url)
