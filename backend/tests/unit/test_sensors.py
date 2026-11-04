from fastapi.testclient import TestClient

from app.series.models import Series


def test_sensor_crud(admin_client: TestClient, series: Series):
    response = admin_client.post(
        "/api/v1/sensors/", json={"name": "PV-01", "seriesId": series.id}
    )
    assert response.status_code == 201
    sensor = response.json()
    assert sensor["name"] == "PV-01"
    assert sensor["seriesId"] == series.id

    response = admin_client.get("/api/v1/sensors/")
    assert response.json()["sensors"] == [sensor]

    response = admin_client.get(f"/api/v1/sensors/{sensor['id']}")
    assert response.json() == sensor

    response = admin_client.delete(f"/api/v1/sensors/{sensor['id']}")
    assert response.status_code == 204
    assert admin_client.get(f"/api/v1/sensors/{sensor['id']}").status_code == 404


def test_sensor_with_unknown_series_rejected(admin_client: TestClient):
    response = admin_client.post(
        "/api/v1/sensors/", json={"name": "PV-01", "seriesId": 999}
    )
    assert response.status_code == 422


def test_missing_sensor_returns_404(admin_client: TestClient):
    assert admin_client.get("/api/v1/sensors/999").status_code == 404
    assert admin_client.delete("/api/v1/sensors/999").status_code == 404
