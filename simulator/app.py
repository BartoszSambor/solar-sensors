"""IoT sensor simulator: sends generated measurements to the main backend over HTTPS,
authenticated with a sensor's X-API-Key, like a real device would.

Runs in the main compose stack; the frontend nginx routes /simulator/ here.
One run at a time, kept in memory. The frontend starts it and polls its status.
"""

import asyncio
import os
import random
from datetime import UTC, datetime
from typing import Literal

import httpx2 as httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from pydantic.alias_generators import to_camel


def _env_list(name: str, default: str = "") -> list[str]:
    items = os.environ.get(name, default).split(",")
    return [s.strip().rstrip("/") for s in items if s.strip()]


# Main backends the simulator may send to (first = default); empty = any.
API_URLS = _env_list("API_URLS")
# Off only for local development against Caddy's self-signed localhost certificate.
TLS_VERIFY = os.environ.get("TLS_VERIFY", "true").lower() != "false"
# Pause between requests: stays under the main nginx rate limit
# (300 requests/min per IP).
SEND_INTERVAL = 0.25


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RunCreate(CamelModel):
    api_url: HttpUrl
    api_key: str = Field(min_length=1)
    count: int = Field(ge=1, le=10000)
    min_value: float = 0
    max_value: float = 100

    @model_validator(mode="after")
    def _check_range(self) -> "RunCreate":
        if self.min_value > self.max_value:
            raise ValueError("minValue must be <= maxValue")
        return self


class RunStatus(CamelModel):
    running: bool = False
    total: int = 0
    sent: int = 0
    failed: int = 0
    last_error: str | None = None
    api_urls: list[str] = API_URLS


status = RunStatus()
task: asyncio.Task[None] | None = None

app = FastAPI(title="Solar Sensors Simulator")


def _error(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"{exc.response.status_code}: {exc.response.text[:200]}"
    return str(exc) or type(exc).__name__


async def _run(run: RunCreate, api_url: str) -> None:
    low, high = run.min_value, run.max_value
    value = (low + high) / 2
    try:
        async with httpx.AsyncClient(
            base_url=api_url,
            headers={"X-API-Key": run.api_key},
            verify=TLS_VERIFY,
            timeout=10,
        ) as client:
            for _ in range(run.count):
                # Random walk within the range, like a slowly changing physical value.
                value += random.uniform(-0.05, 0.05) * (high - low)
                value = min(max(value, low), high)
                now = datetime.now(UTC).isoformat()
                body = {"value": round(value, 2), "timestamp": now}
                try:
                    response = await client.post("/api/measurements", json=body)
                    response.raise_for_status()
                    status.sent += 1
                except httpx.HTTPError as exc:
                    status.failed += 1
                    status.last_error = _error(exc)
                    # Wrong key: every further request would fail too.
                    if (
                        isinstance(exc, httpx.HTTPStatusError)
                        and exc.response.status_code == 401
                    ):
                        break
                await asyncio.sleep(SEND_INTERVAL)
    finally:
        status.running = False


class Health(BaseModel):
    status: Literal["ok"] = "ok"


@app.get("/api/health")
async def health() -> Health:
    return Health()


@app.get("/api/run")
async def get_run() -> RunStatus:
    return status


@app.post("/api/run", status_code=201)
async def start_run(run: RunCreate) -> RunStatus:
    global status, task
    if status.running:
        raise HTTPException(409, "A run is already in progress")
    api_url = str(run.api_url).rstrip("/")
    if API_URLS and api_url not in API_URLS:
        allowed = ", ".join(API_URLS)
        raise HTTPException(422, f"API URL not allowed; use one of: {allowed}")
    status = RunStatus(running=True, total=run.count)
    task = asyncio.create_task(_run(run, api_url))
    return status


@app.delete("/api/run")
async def stop_run() -> RunStatus:
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    return status
