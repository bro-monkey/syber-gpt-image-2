# CyberGen Image Site

React frontend plus a FastAPI backend for Sub2API/OpenAI-compatible image generation.

Local services detected on this machine:

- Sub2API: `http://127.0.0.1:9878`, OpenAI-compatible base URL `http://127.0.0.1:9878/v1`
- cli-proxy-api: `http://127.0.0.1:8389`

The app stores the Sub2API key in the backend SQLite database, calls `/v1/images/generations` for generation, `/v1/images/edits` for edits, and reads balance/usage from `/v1/usage`.

The inspiration feed syncs GPT-Image-2 cases from:

```text
https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts/blob/main/README.md
```

By default the backend parses the README on startup and refreshes it every 6 hours.

## Run

```bash
npm install
python3 -m pip install -r backend/requirements.txt
npm run backend
npm run dev
```

Open `http://127.0.0.1:3000`, then save your Sub2API key in `API Config`.

## Backend

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Important endpoints:

- `GET /api/account`
- `GET /api/balance`
- `GET /api/history`
- `POST /api/images/generate`
- `POST /api/images/edit`
- `PUT /api/config`
- `GET /api/inspirations`
- `POST /api/inspirations/sync`

Generated image files are stored under `backend/storage/images`; uploaded edit references are stored under `backend/storage/uploads`.

## Tests

```bash
PYTHONPATH=backend pytest backend/tests
npm run build
```
