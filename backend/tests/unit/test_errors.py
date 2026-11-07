from fastapi.testclient import TestClient

from app.main import app
from app.series.models import Series

SERIES = {"name": "Humidity", "minValue": 0, "maxValue": 100, "color": "#1f77b4"}


def assert_problem(response, status: int) -> dict:
    assert response.status_code == status
    assert response.headers["content-type"] == "application/problem+json"
    problem = response.json()
    assert problem["status"] == status
    assert problem["title"]
    return problem


def test_not_found_is_problem(client: TestClient):
    problem = assert_problem(client.get("/api/series/999"), 404)
    assert problem["detail"] == "Series not found"
    assert problem["instance"] == "/api/series/999"


def test_unauthorized_is_problem(client: TestClient):
    response = client.post("/api/series", json=SERIES)
    assert_problem(response, 401)
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_syntax_errors_are_400(admin_client: TestClient):
    response = admin_client.post(
        "/api/series",
        content=b"{not json",
        headers={"Content-Type": "application/json"},
    )
    assert_problem(response, 400)

    response = admin_client.post("/api/series", json={"name": "X"})
    problem = assert_problem(response, 400)
    fields = {e["field"] for e in problem["errors"]}
    assert {"minValue", "maxValue", "color"} <= fields

    response = admin_client.post("/api/series", json={**SERIES, "minValue": "low"})
    assert_problem(response, 400)


def test_rule_violations_are_422(admin_client: TestClient):
    response = admin_client.post("/api/series", json={**SERIES, "minValue": 100})
    problem = assert_problem(response, 422)
    assert problem["errors"][0]["message"]


def test_unsupported_media_type(admin_client: TestClient):
    response = admin_client.post(
        "/api/series",
        content=b"<series/>",
        headers={"Content-Type": "application/xml"},
    )
    assert_problem(response, 415)


def test_not_acceptable(client: TestClient, series: Series):
    response = client.get("/api/series", headers={"Accept": "application/xml"})
    assert response.status_code == 406
    for accept in (
        "application/json",
        "application/*",
        "*/*",
        "text/html, application/json;q=0.5",
    ):
        response = client.get("/api/series", headers={"Accept": accept})
        assert response.status_code == 200, accept
    response = client.get("/api/series", headers={"Accept": "application/json;q=0"})
    assert response.status_code == 406


def test_docs_are_not_negotiated(client: TestClient):
    assert client.get("/api/docs", headers={"Accept": "text/html"}).status_code == 200


def test_openapi_documents_problem_errors():
    schema = app.openapi()
    assert "HTTPValidationError" not in schema["components"]["schemas"]
    responses = schema["paths"]["/api/series/{series_id}"]["get"]["responses"]
    assert "application/problem+json" in responses["404"]["content"]
    assert "422" not in responses
