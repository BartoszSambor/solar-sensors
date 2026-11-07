# Solar Sensors

Full-stack app: FastAPI + PostgreSQL backend, React + MUI frontend served by nginx, behind Caddy (HTTPS).

## Run

```bash
cp .env.example .env
docker compose up -d --build
```

- App: https://localhost (http redirects to https)
- API docs: https://localhost/api/docs
- Login: `FIRST_SUPERUSER_USERNAME` / `FIRST_SUPERUSER_PASSWORD` from `.env`

On start the backend applies migrations and creates the first user from `.env`.

## HTTPS

Caddy (`caddy/Caddyfile`) is the public entry point.

- `SITE_ADDRESS=<domain>`: Caddy gets and renews a Let's Encrypt certificate automatically. The domain must point at the server and ports 80 and 443 must be open.

Certificates live in the `caddy_data` volume.

## User accounts

Every account is an admin; anonymous visitors get read-only access. There is no sign-up. Accounts are managed with a CLI inside the backend container:

```bash
docker compose exec backend python -m app.manage create-user <username>
docker compose exec backend python -m app.manage delete-user <username>
```

`create-user` prompts for the password. For scripts, pipe it in with `--password-stdin` (and `exec -T`).

## Sensors

Each sensor (IoT device) authenticates with its own API key. The key is returned only once, in the response to `POST /api/sensors` (the UI shows it in a dialog).

The device sends measurements with the key:
```bash
curl -X POST https://localhost/api/measurements \
  -H "X-API-Key: <key>" -H "Content-Type: application/json" \
  -d '{"value": 21.5, "timestamp": "2026-11-05T12:00:00Z"}'
```

## Simulator

`simulator/` is a small service that acts as IoT sensors: it sends generated measurements to the app's HTTPS address with a sensor's API key. It runs in the same compose stack; nginx routes `/simulator/` to it, and the Simulator page (signed-in users) controls it.

Allowed target addresses come from `SIMULATOR_API_URLS` in `.env`. Locally that is `https://host.docker.internal` (the app as seen from a container).

## Structure

```
backend/    FastAPI app (app/), Alembic migrations (alembic/), tests (tests/)
            dev scripts (scripts/)
docs/       database.mmd - Mermaid ER diagram, regenerated from the models by pre-commit
caddy/      Caddyfile - HTTPS reverse proxy
simulator/  IoT sensor simulator (FastAPI), routed at /simulator/
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
npm run generate-client  # regenerate src/client from the running API (https://localhost)
```

## Code quality

```bash
pre-commit install
pre-commit run --all-files
```
