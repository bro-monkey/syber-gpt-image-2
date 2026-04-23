from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .db import Database
from .inspirations import run_inspiration_sync_loop, sync_inspirations
from .provider import OpenAICompatibleImageClient, ProviderError
from .settings import Settings
from .storage import save_provider_image, save_upload


class ConfigUpdate(BaseModel):
    api_key: str | None = None
    clear_api_key: bool = False
    base_url: str | None = None
    usage_path: str | None = None
    model: str | None = None
    default_size: str | None = None
    default_quality: str | None = None
    user_name: str | None = None


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    model: str | None = None
    size: str | None = None
    quality: str | None = None
    n: int = Field(default=1, ge=1, le=4)
    background: str | None = None
    output_format: str | None = None


def create_app(
    settings: Settings | None = None,
    provider: OpenAICompatibleImageClient | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.ensure_directories()
    db = Database(settings.database_path)
    db.init(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.inspiration_sync_on_startup or settings.inspiration_sync_interval_seconds > 0:
            app.state.inspiration_task = asyncio.create_task(run_inspiration_sync_loop(app))
        try:
            yield
        finally:
            task = app.state.inspiration_task
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    app = FastAPI(title="CyberGen Backend", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.db = db
    app.state.provider = provider or OpenAICompatibleImageClient(settings.request_timeout_seconds)
    app.state.inspiration_task = None
    app.state.last_inspiration_sync = None
    app.state.last_inspiration_sync_error = None
    app.dependency_overrides[_db] = lambda: app.state.db
    app.dependency_overrides[_settings] = lambda: app.state.settings
    app.dependency_overrides[_provider] = lambda: app.state.provider

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        return {
            "ok": True,
            "sub2api_base_url": app.state.db.get_config()["base_url"],
            "detected": {
                "sub2api": "http://127.0.0.1:9878",
                "cli_proxy_api": "http://127.0.0.1:8389",
            },
            "inspirations": db.inspiration_stats(),
            "last_inspiration_sync_error": app.state.last_inspiration_sync_error,
        }

    @app.get("/api/config")
    async def get_config(db: Database = Depends(_db)) -> dict[str, Any]:
        return _public_config(db.get_config())

    @app.put("/api/config")
    async def update_config(payload: ConfigUpdate, db: Database = Depends(_db)) -> dict[str, Any]:
        updates = payload.model_dump(exclude_unset=True)
        clear_api_key = bool(updates.pop("clear_api_key", False))
        if clear_api_key:
            updates["api_key"] = ""
        elif "api_key" in updates and updates["api_key"] == "":
            updates.pop("api_key")
        if "base_url" in updates and updates["base_url"]:
            updates["base_url"] = updates["base_url"].rstrip("/")
        config = db.update_config(updates)
        return _public_config(config)

    @app.post("/api/config/test")
    async def test_config(
        db: Database = Depends(_db),
        provider: OpenAICompatibleImageClient = Depends(_provider),
    ) -> dict[str, Any]:
        try:
            return await provider.test_connection(db.get_config())
        except ProviderError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    @app.get("/api/account")
    async def account(
        db: Database = Depends(_db),
        provider: OpenAICompatibleImageClient = Depends(_provider),
    ) -> dict[str, Any]:
        config = db.get_config()
        usage = await _safe_usage(provider, config)
        return {
            "user": {
                "name": config["user_name"],
                "api_key_set": bool(config["api_key"]),
                "model": config["model"],
                "base_url": config["base_url"],
            },
            "balance": usage,
            "stats": db.stats(),
        }

    @app.get("/api/balance")
    async def balance(
        db: Database = Depends(_db),
        provider: OpenAICompatibleImageClient = Depends(_provider),
    ) -> dict[str, Any]:
        return await _safe_usage(provider, db.get_config())

    @app.get("/api/ledger")
    async def ledger(limit: int = 20, db: Database = Depends(_db)) -> dict[str, Any]:
        return {"items": db.list_ledger(limit)}

    @app.get("/api/history")
    async def history(limit: int = 30, offset: int = 0, q: str = "", db: Database = Depends(_db)) -> dict[str, Any]:
        return {"items": db.list_history(limit=limit, offset=offset, q=q)}

    @app.get("/api/inspirations")
    async def inspirations(
        limit: int = 48,
        offset: int = 0,
        q: str = "",
        section: str = "",
        db: Database = Depends(_db),
    ) -> dict[str, Any]:
        return {"items": db.list_inspirations(limit=limit, offset=offset, q=q, section=section)}

    @app.get("/api/inspirations/stats")
    async def inspiration_stats(db: Database = Depends(_db)) -> dict[str, Any]:
        return {
            **db.inspiration_stats(),
            "source_url": settings.inspiration_source_url,
            "sync_interval_seconds": settings.inspiration_sync_interval_seconds,
            "last_sync": app.state.last_inspiration_sync,
            "last_error": app.state.last_inspiration_sync_error,
        }

    @app.post("/api/inspirations/sync")
    async def inspiration_sync(
        db: Database = Depends(_db),
        settings: Settings = Depends(_settings),
    ) -> dict[str, Any]:
        try:
            result = await sync_inspirations(settings, db)
            app.state.last_inspiration_sync = result
            app.state.last_inspiration_sync_error = None
            return result
        except Exception as exc:
            app.state.last_inspiration_sync_error = str(exc)
            raise HTTPException(status_code=502, detail=f"Inspiration sync failed: {exc}") from exc

    @app.get("/api/history/{history_id}")
    async def history_detail(history_id: str, db: Database = Depends(_db)) -> dict[str, Any]:
        record = db.get_history(history_id)
        if record is None:
            raise HTTPException(status_code=404, detail="History item not found")
        return record

    @app.delete("/api/history/{history_id}")
    async def delete_history(history_id: str, db: Database = Depends(_db)) -> dict[str, Any]:
        deleted = db.delete_history(history_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="History item not found")
        return {"ok": True}

    @app.post("/api/images/generate")
    async def generate_image(
        request: GenerateRequest,
        db: Database = Depends(_db),
        settings: Settings = Depends(_settings),
        provider: OpenAICompatibleImageClient = Depends(_provider),
    ) -> dict[str, Any]:
        config = db.get_config()
        payload = _image_payload(config, request)
        try:
            response = await provider.generate_image(config, payload)
            records = await _persist_image_response(
                db,
                settings,
                mode="generate",
                prompt=request.prompt,
                model=payload["model"],
                size=payload["size"],
                quality=payload["quality"],
                provider_response=response,
            )
            return {"items": records, "provider": {"created": response.get("created"), "usage": response.get("usage")}}
        except ProviderError as exc:
            _record_failed_history(db, "generate", request.prompt, payload, exc.message, exc.payload)
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
        except Exception as exc:
            _record_failed_history(db, "generate", request.prompt, payload, str(exc), None)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/api/images/edit")
    async def edit_image(
        prompt: Annotated[str, Form(min_length=1, max_length=8000)],
        image: Annotated[list[UploadFile], File()],
        mask: Annotated[UploadFile | None, File()] = None,
        model: Annotated[str | None, Form()] = None,
        size: Annotated[str | None, Form()] = None,
        quality: Annotated[str | None, Form()] = None,
        n: Annotated[int, Form(ge=1, le=4)] = 1,
        db: Database = Depends(_db),
        settings: Settings = Depends(_settings),
        provider: OpenAICompatibleImageClient = Depends(_provider),
    ) -> dict[str, Any]:
        config = db.get_config()
        saved_uploads = [await save_upload(settings, upload) for upload in image]
        saved_mask = await save_upload(settings, mask) if mask else None
        fields = {
            "model": model or config["model"],
            "prompt": prompt,
            "size": size or config["default_size"],
            "quality": quality or config["default_quality"],
            "n": str(n),
            "response_format": "b64_json",
        }
        upload_files = [
            (item["filename"], Path(item["path"]).read_bytes(), item["content_type"])
            for item in saved_uploads
        ]
        mask_file = None
        if saved_mask:
            mask_file = (saved_mask["filename"], Path(saved_mask["path"]).read_bytes(), saved_mask["content_type"])

        try:
            response = await provider.edit_image(config, fields, upload_files, mask_file)
            records = await _persist_image_response(
                db,
                settings,
                mode="edit",
                prompt=prompt,
                model=fields["model"],
                size=fields["size"],
                quality=fields["quality"],
                provider_response=response,
                input_image_url=saved_uploads[0]["url"] if saved_uploads else None,
                input_image_path=saved_uploads[0]["path"] if saved_uploads else None,
            )
            return {"items": records, "provider": {"created": response.get("created"), "usage": response.get("usage")}}
        except ProviderError as exc:
            _record_failed_history(db, "edit", prompt, fields, exc.message, exc.payload)
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
        except Exception as exc:
            _record_failed_history(db, "edit", prompt, fields, str(exc), None)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app


def _db() -> Database:
    raise RuntimeError("Dependency should be overridden by FastAPI")


def _settings() -> Settings:
    raise RuntimeError("Dependency should be overridden by FastAPI")


def _provider() -> OpenAICompatibleImageClient:
    raise RuntimeError("Dependency should be overridden by FastAPI")


def _public_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_url": config["base_url"],
        "usage_path": config["usage_path"],
        "model": config["model"],
        "default_size": config["default_size"],
        "default_quality": config["default_quality"],
        "user_name": config["user_name"],
        "api_key_set": bool(config["api_key"]),
        "api_key_hint": _mask_key(config["api_key"]),
    }


def _mask_key(api_key: str) -> str:
    if not api_key:
        return ""
    if len(api_key) <= 10:
        return f"{api_key[:2]}***{api_key[-2:]}"
    return f"{api_key[:6]}...{api_key[-4:]}"


def _image_payload(config: dict[str, Any], request: GenerateRequest) -> dict[str, Any]:
    payload = {
        "model": request.model or config["model"],
        "prompt": request.prompt,
        "size": request.size or config["default_size"],
        "quality": request.quality or config["default_quality"],
        "n": request.n,
        "response_format": "b64_json",
    }
    if request.background:
        payload["background"] = request.background
    if request.output_format:
        payload["output_format"] = request.output_format
    return payload


async def _persist_image_response(
    db: Database,
    settings: Settings,
    *,
    mode: str,
    prompt: str,
    model: str,
    size: str,
    quality: str,
    provider_response: dict[str, Any],
    input_image_url: str | None = None,
    input_image_path: str | None = None,
) -> list[dict[str, Any]]:
    data = provider_response.get("data")
    if not isinstance(data, list) or not data:
        raise ValueError("Provider response did not contain image data")

    records = []
    for item in data:
        if not isinstance(item, dict):
            continue
        history_id = uuid4().hex
        saved = await save_provider_image(settings, history_id, item)
        record = db.create_history(
            {
                "id": history_id,
                "mode": mode,
                "prompt": prompt,
                "model": model,
                "size": size,
                "quality": quality,
                "status": "succeeded",
                "image_url": saved["url"],
                "image_path": saved["path"],
                "input_image_url": input_image_url,
                "input_image_path": input_image_path,
                "revised_prompt": item.get("revised_prompt"),
                "usage": provider_response.get("usage"),
                "provider_response": {"created": provider_response.get("created"), "source_url": saved.get("source_url")},
            }
        )
        db.add_ledger_entry(
            {
                "event_type": mode,
                "amount": 0,
                "description": f"{mode.upper()} {model}",
                "history_id": record["id"],
                "metadata": {"size": size, "quality": quality},
            }
        )
        records.append(record)
    if not records:
        raise ValueError("Provider response image data was empty")
    return records


def _record_failed_history(
    db: Database,
    mode: str,
    prompt: str,
    payload: dict[str, Any],
    message: str,
    provider_response: Any | None,
) -> None:
    db.create_history(
        {
            "mode": mode,
            "prompt": prompt,
            "model": payload.get("model", ""),
            "size": payload.get("size", ""),
            "quality": payload.get("quality", ""),
            "status": "failed",
            "error": message,
            "provider_response": provider_response,
        }
    )


async def _safe_usage(provider: OpenAICompatibleImageClient, config: dict[str, Any]) -> dict[str, Any]:
    if not config.get("api_key"):
        return {"ok": False, "remaining": None, "message": "API Key not configured", "raw": None}
    try:
        return await provider.usage(config)
    except ProviderError as exc:
        return {"ok": False, "remaining": None, "message": exc.message, "raw": exc.payload}


app = create_app()
