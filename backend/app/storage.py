from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from fastapi import UploadFile

from .settings import Settings


DATA_URL_RE = re.compile(r"^data:image/(?P<kind>png|jpeg|jpg|webp);base64,(?P<data>.+)$", re.I | re.S)


async def save_upload(settings: Settings, upload: UploadFile) -> dict[str, str]:
    suffix = _suffix_from_name(upload.filename, ".png")
    filename = f"{uuid4().hex}{suffix}"
    path = settings.uploads_dir / filename
    content = await upload.read()
    path.write_bytes(content)
    return {
        "path": str(path),
        "url": f"/storage/uploads/{filename}",
        "filename": upload.filename or filename,
        "content_type": upload.content_type or "application/octet-stream",
    }


async def save_provider_image(settings: Settings, history_id: str, item: dict[str, Any]) -> dict[str, str | None]:
    b64_json = item.get("b64_json")
    if isinstance(b64_json, str) and b64_json.strip():
        extension, raw = _decode_base64_payload(b64_json)
        filename = f"{history_id}{extension}"
        path = settings.images_dir / filename
        path.write_bytes(raw)
        return {"path": str(path), "url": f"/storage/images/{filename}", "source_url": None}

    image_url = item.get("url")
    if isinstance(image_url, str) and image_url.strip():
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            response = await client.get(image_url)
            response.raise_for_status()
        extension = _suffix_from_content_type(response.headers.get("content-type")) or _suffix_from_name(image_url, ".png")
        filename = f"{history_id}{extension}"
        path = settings.images_dir / filename
        path.write_bytes(response.content)
        return {"path": str(path), "url": f"/storage/images/{filename}", "source_url": image_url}

    raise ValueError("Provider response did not contain b64_json or url")


def _decode_base64_payload(value: str) -> tuple[str, bytes]:
    stripped = value.strip()
    match = DATA_URL_RE.match(stripped)
    if match:
        kind = match.group("kind").lower()
        extension = ".jpg" if kind == "jpeg" else f".{kind}"
        stripped = match.group("data").strip()
    else:
        extension = ".png"
    return extension, base64.b64decode(stripped)


def _suffix_from_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    normalized = content_type.split(";", 1)[0].strip().lower()
    return {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
    }.get(normalized)


def _suffix_from_name(name: str | None, default: str) -> str:
    if not name:
        return default
    suffix = Path(name.split("?", 1)[0]).suffix.lower()
    return suffix if suffix in {".png", ".jpg", ".jpeg", ".webp"} else default
