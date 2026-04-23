from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.inspirations import parse_inspiration_markdown
from app.main import create_app, _db, _provider, _settings
from app.settings import Settings


PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


class FakeProvider:
    async def test_connection(self, config: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "models": ["gpt-image-2"], "raw": {"data": [{"id": "gpt-image-2"}]}}

    async def usage(self, config: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "remaining": 12.5, "raw": {"remaining": 12.5, "unit": "USD"}}

    async def generate_image(self, config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        assert payload["model"] == "gpt-image-2"
        return {"created": 123, "data": [{"b64_json": PNG_B64, "revised_prompt": "revised"}], "usage": {"total_tokens": 1}}

    async def edit_image(
        self,
        config: dict[str, Any],
        fields: dict[str, Any],
        images: list[tuple[str, bytes, str]],
        mask: tuple[str, bytes, str] | None = None,
    ) -> dict[str, Any]:
        assert images
        return {"created": 124, "data": [{"b64_json": PNG_B64}], "usage": {"total_tokens": 2}}


def make_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        backend_dir=tmp_path,
        database_path=tmp_path / "data" / "app.sqlite3",
        storage_dir=tmp_path / "storage",
        provider_base_url="http://127.0.0.1:9878/v1",
        provider_usage_path="/v1/usage",
        image_model="gpt-image-2",
        default_size="1024x1024",
        default_quality="medium",
        user_name="tester",
        cors_origins=["*"],
        request_timeout_seconds=10,
        inspiration_source_url="https://example.com/README.md",
        inspiration_sync_interval_seconds=0,
        inspiration_sync_on_startup=False,
    )
    app = create_app(settings=settings, provider=FakeProvider())
    app.dependency_overrides[_db] = lambda: app.state.db
    app.dependency_overrides[_settings] = lambda: app.state.settings
    app.dependency_overrides[_provider] = lambda: app.state.provider
    return TestClient(app)


def test_config_masks_api_key(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    response = client.put("/api/config", json={"api_key": "sk-test-123456", "user_name": "Neo"})
    assert response.status_code == 200
    data = response.json()
    assert data["api_key_set"] is True
    assert data["api_key_hint"] == "sk-tes...3456"
    assert data["user_name"] == "Neo"


def test_generate_persists_image_and_history(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.put("/api/config", json={"api_key": "sk-test-123456"})

    response = client.post("/api/images/generate", json={"prompt": "neon city"})

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["status"] == "succeeded"
    assert item["image_url"].startswith("/storage/images/")
    assert Path(item["image_path"]).exists()

    history = client.get("/api/history").json()["items"]
    assert len(history) == 1
    assert history[0]["prompt"] == "neon city"


def test_edit_persists_upload_and_result(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.put("/api/config", json={"api_key": "sk-test-123456"})

    response = client.post(
        "/api/images/edit",
        data={"prompt": "make it cyberpunk"},
        files={"image": ("source.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["mode"] == "edit"
    assert item["input_image_url"].startswith("/storage/uploads/")
    assert Path(item["input_image_path"]).exists()


def test_account_includes_balance_and_stats(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.put("/api/config", json={"api_key": "sk-test-123456"})
    client.post("/api/images/generate", json={"prompt": "one"})

    response = client.get("/api/account")

    assert response.status_code == 200
    data = response.json()
    assert data["balance"]["remaining"] == 12.5
    assert data["stats"]["total"] == 1


def test_parse_inspiration_markdown() -> None:
    markdown = """
## Portrait & Photography Cases

### Case 1: [Convenience Store Neon Portrait](https://x.com/demo/status/1) (by [@demo](https://x.com/demo))

| Output |
| :----: |
| <img src="./images/portrait_case1/output.jpg" width="300" alt="Output image"> |

**Prompt:**

```
35mm film photography, neon signs, authentic grain
```
"""
    items = parse_inspiration_markdown(
        markdown,
        "https://raw.githubusercontent.com/EvoLinkAI/awesome-gpt-image-2-prompts/main/README.md",
    )

    assert len(items) == 1
    assert items[0]["section"] == "Portrait & Photography Cases"
    assert items[0]["title"] == "Convenience Store Neon Portrait"
    assert items[0]["author"] == "@demo"
    assert items[0]["source_link"] == "https://x.com/demo/status/1"
    assert items[0]["image_url"].endswith("/images/portrait_case1/output.jpg")
    assert "35mm film" in items[0]["prompt"]


def test_manual_inspiration_sync_endpoint(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    db = client.app.state.db
    db.upsert_inspirations(
        "https://example.com/README.md",
        [
            {
                "id": "abc",
                "source_item_id": "abc",
                "section": "UI",
                "title": "Mockup",
                "author": "@demo",
                "prompt": "make a UI",
                "image_url": "https://example.com/image.jpg",
                "source_link": "https://example.com/post",
                "raw": {},
            }
        ],
    )

    response = client.get("/api/inspirations")

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["title"] == "Mockup"
