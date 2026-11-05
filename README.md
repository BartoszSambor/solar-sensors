# Solar Sensors

Full-stack app: FastAPI + PostgreSQL backend, React + MUI frontend served by nginx.

## Run

```bash
cp .env.example .env
docker compose up -d --build
```

- App: http://localhost
- API docs: http://localhost/api/v1/docs
- Login: `FIRST_SUPERUSER_USERNAME` / `FIRST_SUPERUSER_PASSWORD` from `.env`

On start the backend applies migrations and creates the first user from `.env`.

## User accounts

Every account is an admin; anonymous visitors get read-only access. There is no sign-up. Accounts are managed with a CLI inside the backend container:

```bash
docker compose exec backend python -m app.manage create-user <username>
docker compose exec backend python -m app.manage delete-user <username>
```

`create-user` prompts for the password. For scripts, pipe it in with `--password-stdin` (and `exec -T`).

## Sensors

Each sensor (IoT device) authenticates with its own API key. The key is returned only once, in the response to `POST /api/v1/sensors/` (the UI shows it in a dialog).

The device sends measurements with the key:
```bash
curl -X POST http://localhost/api/measurements \
  -H "X-API-Key: <key>" -H "Content-Type: application/json" \
  -d '{"value": 21.5, "timestamp": "2026-11-05T12:00:00Z"}'
```

## Structure

```
backend/    FastAPI app (app/), Alembic migrations (alembic/), tests (tests/)
            dev scripts (scripts/)
docs/       database.mmd - Mermaid ER diagram, regenerated from the models by pre-commit
frontend/   React app (src/), generated API client (src/client/), nginx config
```

## Backend development

```bash
cd backend
uv sync                         # install deps incl. dev tools
uv run pytest tests/unit        # unit tests (SQLite)
uv run pytest tests/integration # integration tests (Postgres via testcontainers, needs Docker)
uv run alembic revision --autogenerate -m "message"  # new migration
```

Add a dependency: `uv add <package>`.

## Frontend development

Requires Node.js >= 22.12 (Vite 8).

```bash
cd frontend
npm install
npm run dev              # dev server
npm run lint             # biome
npm run generate-client  # regenerate src/client from the running API (http://localhost)
```

## Code quality

```bash
pre-commit install
pre-commit run --all-files
```
