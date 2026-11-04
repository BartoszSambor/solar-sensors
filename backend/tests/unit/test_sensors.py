from fastapi.testclient import TestClient

from app.series.models import Series


def test_sensor_crud(client: TestClient, series: Series):
    response = client.post(
        "/api/v1/sensors/", json={"name": "PV-01", "seriesId": series.id}
    )
    assert response.status_code == 201
    sensor = response.json()
    assert sensor["name"] == "PV-01"
    assert sensor["seriesId"] == series.id

    response = client.get("/api/v1/sensors/")
    assert response.json()["sensors"] == [sensor]

    response = client.get(f"/api/v1/sensors/{sensor['id']}")
    assert response.json() == sensor

    response = client.delete(f"/api/v1/sensors/{sensor['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/sensors/{sensor['id']}").status_code == 404


def test_sensor_with_unknown_series_rejected(client: TestClient):
    response = client.post("/api/v1/sensors/", json={"name": "PV-01", "seriesId": 999})
    assert response.status_code == 422


def test_missing_sensor_returns_404(client: TestClient):
    assert client.get("/api/v1/sensors/999").status_code == 404
    assert client.delete("/api/v1/sensors/999").status_code == 404
