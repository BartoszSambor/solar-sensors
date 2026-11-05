"""Anonymous users can read data; writes and the users list need a bearer token.

Adding measurements is the exception: it needs a sensor's X-API-Key instead
(see test_measurements.py).
"""

import pytest
from fastapi.testclient import TestClient

from app.series.models import Series

PUBLIC_READS = [
    "/api/series",
    "/api/v1/sensors/",
    "/api/measurements",
]

LOGIN_REQUIRED = [
    ("GET", "/api/v1/users/"),
    ("POST", "/api/series"),
    ("PUT", "/api/series/1"),
    ("DELETE", "/api/series/1"),
    ("POST", "/api/v1/sensors/"),
    ("DELETE", "/api/v1/sensors/1"),
]


@pytest.mark.parametrize("url", PUBLIC_READS)
def test_anonymous_can_read(client: TestClient, url: str):
    assert client.get(url).status_code == 200


def test_anonymous_can_read_single_series(client: TestClient, series: Series):
    assert client.get(f"/api/series/{series.id}").status_code == 200


@pytest.mark.parametrize(("method", "url"), LOGIN_REQUIRED)
def test_anonymous_cannot_write(client: TestClient, method: str, url: str):
    response = client.request(method, url, json={})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(("method", "url"), LOGIN_REQUIRED)
def test_revoked_token_cannot_write(admin_client: TestClient, method: str, url: str):
    assert admin_client.post("/auth/logout").status_code == 204
    assert admin_client.request(method, url, json={}).status_code == 401
